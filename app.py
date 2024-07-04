from flask import Flask, request, jsonify

# Creates Flask class instance 
app = Flask(__name__)


@app.route('/chat', methods=['POST'])
def chat():
    # Get the 'message' field from the JSON data in the request
    user_message = request.json.get('message')
    
    # Simulated bot response; replace with actual logic to generate response from Llama 2
    bot_response = "This is a simulated response from the bot."  
    
    # Return a JSON response with the bot's reply
    return jsonify({'response': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
