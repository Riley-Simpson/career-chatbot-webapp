from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

COLAB_API_URL = "YOUR_NGROK_URL_HERE/query"  # Replace with your ngrok URL

@app.route("/query", methods=["POST"])
def query():
    data = request.get_json()
    response = requests.post(COLAB_API_URL, json=data)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run()
