
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext
from llama_index.readers.json import JSONReader
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core.prompts.prompts import SimpleInputPrompt
from huggingface_hub import login
import json 



class chat:
    def __init__(self):
        self.main
    
    
    def hg_login(self):
        api_key = json.load("HUGGING_FACE_TOKEN.json")["access_token"]
        login(token=api_key)
        return print("Succesfully Logged in.")
    
    def main(self):
        pass


chat.hg_login()