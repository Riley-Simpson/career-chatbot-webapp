import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import aiohttp
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chat:
    def __init__(self, local_api_url):
        """
        Initialize the bot with the local API URL.
        """
        self.local_api_url = local_api_url

    async def query(self, query_str):
        """
        Query the API to get information about a query. This is a helper function for the query_to_json function

        @param query_str - The query string to send to the API

        @return The response from the API or "Sorry, something went wrong. Please try again." In this case, the error is logged
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.local_api_url, json={"context": query_str}) as response:
                    response_data = await response.json()
                    return response_data['response']
        except Exception as e:
            logger.error(f"Error communicating with local API: {e}")
            return f"Sorry, something went wrong. Please try again.{e}"

async def create_chat_instance():
    # Note: Ensure the ngrok tunnel is running and retrieve the current public URL
    local_api_url = "https://4ce6-90-194-4-76.ngrok-free.app/chat"
    return Chat(local_api_url)

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
async def chat():
    data = request.json
    user_input = data.get('input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response = await chat_instance.query(user_input)
    return jsonify({"response": response})

@app.before_first_request
async def setup_chat_instance():
    global chat_instance
    chat_instance = await create_chat_instance()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666)
