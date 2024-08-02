import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from pyngrok import ngrok, conf

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
    """
    Send a chat message to a user. This is a wrapper around chat_instance to allow you to use it as a context manager.
    
    Returns: 
        JSON with the response of the chat message or error
    """
    data = request.json
    user_input = data.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response = chat_instance.query(user_input)
    return jsonify({"response": response})

# Start ngrok tunnel using the configuration file ngrok.yml
if __name__ == '__main__':
    # Ensure ngrok is installed
    ngrok_path = "ngrok/ngrok.exe"  

    # Load the ngrok configuration
    ngrok_config = conf.PyngrokConfig(ngrok_path=ngrok_path, config_path="ngrok/ngrok.yml")
    
    try:
        # Start ngrok tunnel using the configuration file
        ngrok_tunnel = ngrok.connect(pyngrok_config=ngrok_config, addr="6666")
    except Exception as e:
        logger.error(f"Failed to start ngrok tunnel: {e}")
        exit(1)

    print("ngrok URL:", ngrok_tunnel.public_url)
    app.run(host='0.0.0.0', port=6666)