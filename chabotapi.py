
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.core.readers.json import JSONReader
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.prompts.prompts import SimpleInputPrompt
from huggingface_hub import login
import json ,torch
from flask import Flask, request, jsonify
from flask_ngrok import run_with_ngrok
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.core import ServiceContext
from llama_index.legacy.embeddings.langchain import LangchainEmbedding

class chat:
    def __init__(self):
        self.dataset = None
        self.llm = None
        self.main

    def hg_login(self):
        with open("HUGGING_FACE_TOKEN.json", "r") as f:
            api_key = json.load(f)["access_token"]
        login(token=api_key)
        return print("Succesfully Logged in.")
    
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
        system_prompt="""
        You are a Career Advisor for students at the University of Strathclyde.
        Your job is to advice students asaccurately as possible based on the data being provided.
        """
        query_wrapper_prompt=SimpleInputPrompt("<|USER|>{query_str}<|ASSISTANT|>")
        self.llm = HuggingFaceLLM(
            context_window=4096,
            max_new_tokens=256,
            generate_kwargs={"temperature": 0.0, "do_sample": False},
            system_prompt=system_prompt,
            query_wrapper_prompt=query_wrapper_prompt,
            tokenizer_name="meta-llama/Llama-2-7b-chat-hf",
            model_name="meta-llama/Llama-2-7b-chat-hf",
            device_map="auto",
            # uncomment this if using CUDA to reduce memory usage
            model_kwargs={"torch_dtype": torch.float16 , "load_in_8bit":True}
        )
        print("LLM Loaded")
        
    
    def main(self):
        self.hg_login()
        self.data_load()
        self.load_model()

chat_instance = chat()
chat_instance.main()


app = Flask(__name__)
run_with_ngrok(app)  # Start ngrok when app is run

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    response = chat_instance.query(data["query"])
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run()