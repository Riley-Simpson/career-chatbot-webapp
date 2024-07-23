import os
import json
from llama_index.core.readers.json import JSONReader
from llama_index.core import SimpleDirectoryReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb

class Dataset:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', collection_name='career_data', predefined_directory_path=None):
        # Initialize the SentenceTransformer model
        self.model = SentenceTransformer(model_name)
        # Initialize Chroma DB
        self.client = chromadb.Client()
        self.collection_name = collection_name
        self.collection = self.client.create_collection(collection_name,metadata={"hnws:space":"cosine"})
        # Predefined directory path in the Colab environment
        self.predefined_directory_path = predefined_directory_path

    def load_data(self, directory_path=None):
        if directory_path is None:
            directory_path = self.predefined_directory_path
        if directory_path is None:
            return {"error": "No directory path provided"}, 400

        try:
            # Clear existing collection
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(self.collection_name, metadata={"hnws:space":"cosine"})

            doc_embedding=[]
            metadatas=[]
            ids=[]
                        
            # Load and process files
            for root, _, files in os.walk(directory_path):
                for file in tqdm(files):
                    print(f"==============Processing {file}==============")
                    file_path = os.path.join(root, file)
                    if file.endswith('.json'):
                        reader = JSONReader(
                            levels_back=0,
                            collapse_length=200,
                            ensure_ascii=False,
                            is_jsonl=False,
                            clean_json=False,
                        )
                        documents = reader.load_data(input_file=file_path, extra_info={})
                    else:
                        reader = SimpleDirectoryReader(root)
                        documents = reader.load_data()
                    
                    print(f"--------------Embedding {file}--------------")
                    for idx, doc in enumerate(documents):
                        doc_text = doc.get_text()
                        doc_embedding = self.model.encode([doc_text])
                        metadatas.append({"doc": doc_text})
                        ids.append(str(idx))

            self.collection.add(embeddings=doc_embedding, metadatas=metadatas, ids=ids)
            
            return {"message": "Dataset Loaded"}, 200
        except Exception as e:
            return {"error": f"Error loading data: {e}"}, 500

    def retrieve_documents(self, query_str):
        try:
            query_embedding = self.model.encode([query_str])
            similarities = self.collection.query(query_embeddings=query_embedding,
                                                 n_results=3)
            retrieved_docs = []                      
            if 'metadatas' in similarities:
                metadatas = similarities['metadatas']
                print("Metadatas:", metadatas)
                
                for metadata in metadatas:
                    # Debugging: Print each metadata to inspect its structure
                    print("Metadata:", metadata)
                    
                    # Check if metadata is a dictionary and contains the 'doc' key
                    if isinstance(metadata, dict) and 'doc' in metadata:
                        document = metadata['doc']
                        retrieved_docs.append(document)
                    else:
                        print("Metadata format is not as expected:", metadata)

            return retrieved_docs
        except Exception as e:
            return {"error": f"Error retrieving documents: {e}"}, 500
# Example usage
if __name__ == "__main__":
    # Initialize the DocumentRetrieval class
    doc_retrieval = Dataset(predefined_directory_path=r'G:\My Drive\Dissertation_Database')

    # Load data into the collection
    load_response = doc_retrieval.load_data()
    print(load_response)

    # Retrieve documents based on a query
    query = "example query"
    retrieve_response = doc_retrieval.retrieve_documents(query)
    print(retrieve_response)

