import requests
import json

def send_query_to_ngrok(query_str, ngrok_url):
    url = f"{ngrok_url}/query"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "query": query_str
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        return response.json()["response"]
    else:
        return f"Error: {response.status_code}, {response.text}"

# Example usage
ngrok_url = "https://bc5a-34-32-199-169.ngrok-free.app/"  # Replace with your actual ngrok URL
query_str = "What are the job opportunities for computer science graduates?"

response = send_query_to_ngrok(query_str, ngrok_url)
print(response)
