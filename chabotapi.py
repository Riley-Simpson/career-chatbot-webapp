import json
import torch
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.core.readers.json import JSONReader
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.prompts.prompts import SimpleInputPrompt
from huggingface_hub import login
from flask import Flask, request, jsonify
from pyngrok import ngrok
from langchain_community.embeddings import HuggingFaceEmbeddings
from llama_index.legacy.embeddings.langchain import LangchainEmbedding



class Chat:
    def __init__(self):
        self.dataset = None
        self.llm = None
        self.service_context = None
        self.index=None
        self.query_engine=None
        

    def hg_login(self):
        with open("HUGGING_FACE_TOKEN.json", "r") as f:
            api_key = json.load(f)["access_token"]
        login(token=api_key)
        print("Successfully Logged in.")
    
    def data_load(self):
        reader = JSONReader(
            levels_back=0,
            collapse_length=200,
            ensure_ascii=False,
            is_jsonl=False,
            clean_json=True,
        )
        self.dataset = reader.load_data(input_file="resume_data.json", extra_info={})
        print("Dataset Loaded")
    
    def load_model(self):
        system_prompt = """
        You are a Career Advisor for students at the University of Strathclyde.
        Your job is to advise students as accurately as possible based on the data being provided.
        """
        query_wrapper_prompt = SimpleInputPrompt("{query_str}")
        self.llm = HuggingFaceLLM(
            context_window=4096,
            max_new_tokens=256,
            generate_kwargs={"temperature": 0.0, "do_sample": False},
            system_prompt=system_prompt,
            query_wrapper_prompt=query_wrapper_prompt,
            tokenizer_name="meta-llama/Llama-2-7b-chat-hf",
            model_name="meta-llama/Llama-2-7b-chat-hf",
            device_map="auto",
            model_kwargs={"torch_dtype": torch.float16, "load_in_8bit": True}
        )
        print("LLM Loaded")
    
    def embed_model(self):
        self.embedded_model=LangchainEmbedding(HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2"))
        return print("Model Embeded")

    def service_context(self):
        self.service_context=ServiceContext.from_defaults(
        chunk_size=1024,
        llm=self.llm,
        embed_model=self.embed_model)
        print("Service Context established")

    def engine_start(self):
        self.index = VectorStoreIndex.from_documents(self.data,service_context=self.service_context)
        self.query_engine= self.index.as_query_engine()
        print("Engine Loaded")

    def query(self, query_str):
        return self.query_engine(query_str)

    def initialize(self):
        self.hg_login()
        self.data_load()
        self.load_model()
        self.embed_model()
        self.service_context()
        self.engine_start()



app = Flask(__name__)

@app.route("/query", methods=["POST"])
def query():
    chat_instance = Chat()
    chat_instance.initialize()
    data = request.get_json()
    response = chat_instance.query(data["query"])
    return jsonify({"response": response})


with open("ngrok.json","r") as f:
    ngrok_api_key = json.load(f)["authtoken"]


if __name__ == "__main__":
    ngrok.set_auth_token(ngrok_api_key)
    public_url = ngrok.connect(5000)
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://0.0.0.0:5000\"")
    app.run(host="0.0.0.0",port=5000)
