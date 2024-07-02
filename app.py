from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    bot_response = "This is a simulated response from the bot."  # Replace with actual Llama 2 response
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
