import json
import requests
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from flask import Flask, request, jsonify
from pyngrok import ngrok

class Chat:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-hf"
        self.api_key = None
        self.embeddings = None
        self.data = None
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def hg_login(self):
        with open("HUGGING_FACE_TOKEN.json", "r") as f:
            self.api_key = json.load(f)["access_token"]
        print("Successfully Logged in.")
    
    def data_load(self):
        with open("resume_data.json", "r") as f:
            self.data = json.load(f)
        documents = [self._create_document_text(doc) for doc in self.data]
        self.embeddings = self.model.encode(documents)
        print("Data and Embeddings Loaded")

    def _create_document_text(self, doc):
        experiences = " ".join(doc.get("experience", []) or [])  # Handle the case when 'experience' is missing
        skills = " ".join(doc.get("skills", []) or [])  # Handle the case when 'skills' is missing
        return f"Experience: {experiences} Skills: {skills}"

    def retrieve_documents(self, query_str, top_k=3):
        query_embedding = self.model.encode([query_str])
        similarities = cosine_similarity(query_embedding, self.embeddings)
        top_k_indices = np.argsort(similarities[0])[-top_k:][::-1]
        retrieved_docs = [self.data[idx] for idx in top_k_indices]
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

@app.route("/query", methods=["POST"])
def query():   
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

