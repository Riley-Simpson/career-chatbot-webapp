import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import asyncio
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chat:
    def __init__(self):
        """
        Initialize the bot. Called by __init__ () to set the bot's local_api_url
        """
        self.local_api_url = "https://4ce6-90-194-4-76.ngrok-free.app/chat"
    async def query(self, query_str):
        """
        Query the API to get information about a query. This is a helper function for the query_to_json function

        @param query_str - The query string to send to the API

        @return The response from the API or Sorry if something went wrong. In this case the error is logged
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.local_api_url, json={"context": query_str}) as response:
                    response_data = await response.json()
                    return response_data['response']
        except Exception as e:
            logger.error(f"Error communicating with local API: {e}")
            return f"Sorry, something went wrong. Please try again, Error communicating with local API.{e}"

chat_instance = Chat()

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666)
