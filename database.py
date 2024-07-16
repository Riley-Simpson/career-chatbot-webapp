import os
import json
from flask import Flask, request, jsonify
from llama_index.core.readers.json import JSONReader
from llama_index import SimpleDirectoryReader
from sentence_transformers import SentenceTransformer
import chromadb
from flask_cors import CORS

database = Flask(__name__)
CORS(database)

# Initialize the SentenceTransformer model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Initialize Chroma DB
client = chromadb.Client()
collection = client.create_collection('resume_data')

def load_data(directory_path):
    try:
        # Clear existing collection
        collection.clear()

        # Load and process files
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.json'):
                    reader = JSONReader(
                        levels_back=0,
                        collapse_length=200,
                        ensure_ascii=False,
                        is_jsonl=False,
                        clean_json=True,
                    )
                    documents = reader.load_data(input_file=file_path, extra_info={})
                else:
                    reader = SimpleDirectoryReader(root)
                    documents = reader.load_data()

                for idx, doc in enumerate(documents):
                    doc_text = doc.get_text()
                    doc_embedding = model.encode([doc_text])
                    collection.add(doc_embedding, metadata={'id': idx, 'doc': doc_text})

        return {"message": "Dataset Loaded"}, 200
    except Exception as e:
        return {"error": f"Error loading data: {e}"}, 500

@database.route("/load_data", methods=["POST"])
def load_data_endpoint():
    data = request.get_json()
    directory_path = data.get("directory_path")
    return jsonify(*load_data(directory_path))

@database.route("/retrieve_documents", methods=["POST"])
def retrieve_documents():
    data = request.get_json()
    query_str = data["query_str"]
    top_k = data.get("top_k", 3)

    try:
        query_embedding = model.encode([query_str])
        similarities = collection.similarity_search(query_embedding, top_k=top_k)

        retrieved_docs = [sim['metadata']['doc'] for sim in similarities]
        return jsonify({"documents": retrieved_docs}), 200

    except Exception as e:
        return jsonify({"error": f"Error retrieving documents: {e}"}), 500

if __name__ == "__main__":
    database.run(host="0.0.0.0", port=5001)
