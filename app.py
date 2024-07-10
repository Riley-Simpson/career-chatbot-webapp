import json
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask import Flask, request, jsonify, render_template
from llama_index.core.readers.json import JSONReader

class Chat:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-hf"
        self.api_key = None
        self.dataset = None
        self.embeddings = None
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def hg_login(self):
        with open("HUGGING_FACE_TOKEN.json", "r") as f:
            self.api_key = json.load(f)["access_token"]
        print("Successfully Logged in.")
    
    def data_load(self):
        url = 'https://github.com/Riley-Simpson/career-chatbot-webapp/blob/main/resume_data.json'
        response = requests.get(url)
        data = response.json()
        reader = JSONReader(
            levels_back=0,
            collapse_length=200,
            ensure_ascii=False,
            is_jsonl=False,
            clean_json=True,
        )
        self.dataset = reader.load_data(input_file=data, extra_info={})
        print("Dataset Loaded")

    def _create_document_text(self, doc):
        experiences = " ".join(doc.get("experience", []) or [])
        skills = " ".join(doc.get("skills", []) or [])
        return f"Experience: {experiences} Skills: {skills}"

    def retrieve_documents(self, query_str, top_k=3):
        documents = [self._create_document_text(doc) for doc in self.dataset]
        self.embeddings = self.model.encode(documents)
        query_embedding = self.model.encode([query_str])
        similarities = cosine_similarity(query_embedding, self.embeddings)
        top_k_indices = np.argsort(similarities[0])[-top_k:][::-1]
        retrieved_docs = [self.dataset[idx] for idx in top_k_indices]
        return retrieved_docs

    def generate_response(self, context):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": context}
        response = requests.post(self.api_url, headers=headers, json=payload)
        return response.json()

    def query(self, query_str):
        retrieved_docs = self.retrieve_documents(query_str)
        context = " ".join([self._create_document_text(doc) for doc in retrieved_docs])
        response = self.generate_response(context)
        return response

    def initialize(self):
        self.hg_login()
        self.data_load()

app = Flask(__name__)
chat_instance = Chat()
chat_instance.initialize()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    response = chat_instance.query(data["query"])
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
