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
        print("Generating Response")
        try:
            response = ollama.chat(
                model= 'llama3:latest',
                messages=[
                    {
                        'role':'user',
                        'content':context
                    }
                ]
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, something went wrong. Please try again."

    def query(self, query_str):
        try:
            retrieved_docs = self.database.retrieve_documents(query_str)
            context = (f"{query_str} Answer the users question using the following informtation : \n {retrieved_docs}")
            return self.generate_response(context)
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return {"error": f"Error retrieving documents: {e}"}    

chat_instance = Chat()


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
