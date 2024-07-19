import requests

# Load data into the data loading app
load_data_response = requests.post("https://8fed-34-138-57-160.ngrok-free.app/load_data")
print(load_data_response.json())

# Send a query to the chat app
query_response = requests.post("http://localhost:5000/query", json={"query": "your query string"})
print(query_response.json())
