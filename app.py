import json
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from database import Dataset
import ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chat:
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        self.database = Dataset(predefined_directory_path=r'G:\My Drive\Dissertation_Database')
        self.database.load_data()
        self.ollama_model = "Llama-3"  

    def generate_response(self, context):
        try:
            response = ollama.chat_completion(
                model=self.ollama_model,
                messages=[{"role": "user", "content": context}],
                max_tokens=500
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, something went wrong. Please try again."

    def query(self, query_str):
        try:
            retrieved_docs = self.database.retrieve_documents(query_str)
            context = " ".join(retrieved_docs)
            return self.generate_response(context)
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return {"error": f"Error retrieving documents: {e}"}
        
    def initialize(self):
        pass

chat_instance = Chat()
chat_instance.initialize()

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    response = chat_instance.query(data["query"])
    if isinstance(response, dict) and "error" in response:
        return jsonify(response)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
