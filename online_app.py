import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chat:
    def __init__(self, local_api_url):
        self.local_api_url = local_api_url

    def query(self, query_str):
        try:
            response = requests.post(self.local_api_url + "/chat", json={"context": query_str})
            response_data = response.json()
            return response_data.get('response', 'No response content')
        except Exception as e:
            logger.error(f"Error communicating with local API: {e}")
            return "Sorry, something went wrong. Please try again."

def create_chat_instance():
    local_api_url = "https://skilled-redbird-needlessly.ngrok-free.app"
    return Chat(local_api_url)

app = Flask(__name__)
CORS(app)

chat_instance = create_chat_instance()

# In-memory storage for active session
active_session = {
    'user': None,
    'expiry': None
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    global active_session

    if not active_session['user'] or active_session['expiry'] < datetime.now():
        # Start new session
        active_session['user'] = request.remote_addr
        active_session['expiry'] = datetime.now() + timedelta(minutes=5)
    elif active_session['user'] != request.remote_addr:
        return jsonify({'response': 'Chat is currently in use by another user. Please wait your turn.'})

    data = request.get_json()
    user_input = data.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response = chat_instance.query(user_input)
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666, threaded=True)
