import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
from PyPDF2 import PdfReader
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Chat:
    def __init__(self, local_api_url):
        """
         Initialize the instance. This is called by __init__ and should not be called directly. The local_api_url is the URL of the API that will be used to make requests to the API.
         
         @param local_api_url - The URL of the API
        """
        self.local_api_url = local_api_url

    def query(self, query_str):
        """
         Query the chat server with query_str and return the response. This is used for debugging and to check the status of the chat
         
         @param query_str - The query string to send to the server
         
         @return The response of the chat or Sorry if something went wrong. In this case you should try again
        """
        try:
            response = requests.post(self.local_api_url + "/chat", json={"context": query_str})
            response_data = response.json()
            return response_data.get('response', 'No response content')
        except Exception as e:
            logger.error(f"Error communicating with local API: {e}")
            return "Sorry, something went wrong. Please try again."

    def upload_resume(self,file):
        try:
            pdf_reader = PdfReader(file)
            text =''
            for page_num in range(len(pdf_reader.pages)()):
                page = pdf_reader.getPage(page_num)                
                text += page.extractText()
            response = requests.post(self.local_api_url + "/upload_resume", json={"resume":text})        
            response_data=response.json()
            return response_data.get('response', 'No response content')
        except Exception as e:
            logger.error(f"Error communicating with local API: {e} \n")
            return "Sorry, something went wrong. Please try again."

        

def create_chat_instance():
    local_api_url = "https://skilled-redbird-needlessly.ngrok-free.app"
    return Chat(local_api_url)

app = Flask(__name__)
CORS(app)

chat_instance = create_chat_instance()

active_session = {
    'user': None,
    'expiry': None
}

@app.route("/")
def index():
    """
     The index page of the web application. It is used to display the main page of the web application.
     
     
     @return The response to the request as a string or HTML document depending on the type of response being returned. If the response is an HTML document it will be returned
    """
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    """
     Send chat message to user. This is a web service call and should be used for anyone who wants to chat a user.
     
     
     @return JSON with response or error message if something went wrong. The user is logged in and a message is
    """
    global active_session

    # If the chatbot is currently in use by another user.
    if not active_session['user'] or active_session['expiry'] < datetime.now():
        # Start new session
        active_session['user'] = request.remote_addr
        active_session['expiry'] = datetime.now() + timedelta(minutes=5)
    elif active_session['user'] != request.remote_addr:
        return jsonify({'response': 'Chat is currently in use by another user. Please wait your turn.'})

    data = request.get_json()
    user_input = data.get('context')
    # If user input is not provided
    if not user_input:
        return jsonify({"error": "No input provided"}), 400

    response = chat_instance.query(user_input)
    return jsonify({"response": response})

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'success': False, 'message': f'No file part: {request.files}'})
    
    file = request.files['resume']
    file_path = os.path.join('/tmp', file.filename)
        
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No selected file'})
    
    try:
        file.save(file_path)
        resume=chat_instance.upload_resume(file_path)
        os.remove(file_path)
        return jsonify({"resume":resume})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# Run the app if the __main__ is called.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6666, threaded=True)
