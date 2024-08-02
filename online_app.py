import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chat:
    def __init__(self):
        """
         Initialize the bot. Called by __init__ () to set the bot's local_api_url
        """
        self.local_api_url = "https://skilled-redbird-needlessly.ngrok-free.app/chat"

    def query(self, query_str):
        """
         Query the API to get information about a query. This is a helper function for the query_to_json function
         
         @param query_str - The query string to send to the API
         
         @return The response from the API or Sorry if something went wrong. In this case the error is logged
        """
        # Send query to locla API and return response.
        try:
            response = requests.post(
                self.local_api_url,
                json={"context": query_str}
            )
            response_data = response.json()
            return response_data['response']
        except Exception as e:
            logger.error(f"Error communicating with local API: {e}")
            return "Sorry, something went wrong. Please try again."

chat_instance = Chat()

app = Flask(__name__)
LOCAL_API_URL = "https://skilled-redbird-needlessly.ngrok-free.app/chat"
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    # Send the input to the local API
    response = requests.post(LOCAL_API_URL, json={'input': user_input})
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666)