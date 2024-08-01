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
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/query", methods=["POST"])
def query():
    """
     Query chat. This is a REST API call. The response is a JSON object with the following keys.
          
     @return JSON object with the response of the query.
    """
    data = request.get_json()
    response = chat_instance.query(data["query"])
    return jsonify({"response": response})

# Run the app with the default port 5000
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)