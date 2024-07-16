import json
import requests
from sentence_transformers import SentenceTransformer
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

class Chat:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-hf"
        self.api_key = None
        self.dataset_url = "http://localhost:5001"
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    def hg_login(self):
        with open("HUGGING_FACE_TOKEN.json", "r") as f:
            self.api_key = json.load(f)["access_token"]
        print("Successfully Logged in.")

    def generate_response(self, context):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        payload = {"inputs": context}
        response = requests.post(self.api_url, headers=headers, json=payload)
        return response.json()

    def query(self, query_str):
        response = requests.post(f"{self.dataset_url}/retrieve_documents", json={"query_str": query_str, "top_k": 3})
        if response.status_code == 200:
            retrieved_docs = response.json().get("documents", [])
            context = " ".join(retrieved_docs)
            return self.generate_response(context)
        else:
            return {"error": "Failed to retrieve documents from dataset app"}

    def initialize(self):
        self.hg_login()

app = Flask(__name__)
CORS(app)
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
