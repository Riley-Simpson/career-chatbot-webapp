import os
import ujson
from llama_index.core import SimpleDirectoryReader
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb


class Dataset:
    def __init__(self, model_name='sentence-transformers/all-MiniLM-L6-v2', collection_name='career_data', predefined_directory_path=None):
        self.model = SentenceTransformer(model_name)
        self.client = chromadb.Client()
        self.collection_name = collection_name
        self.collection = self.client.create_collection(collection_name,metadata={"hnws:space":"cosine"})
        self.predefined_directory_path = predefined_directory_path

    def process_json(self,file):       
        with open(file, 'r') as f:
            json_file = ujson.load(f)
        
       
        def embedded(doc):
            print('flag3')
            return self.model.encode(str(doc)).tolist()
       
        print(f"Adding {file}")
        for idx,doc in enumerate(tqdm(json_file)):
            try:
                self.collection.add(
                    #embeddings=embedded(doc),
                    metadatas={key: ', '.join(value) if isinstance(value, list) else value for key, value in doc.items() if value not in [None, '', []]},
                    ids=f"{file}_{idx}",
                    documents=str(doc))
                
            except Exception as e:
                print(e)

               
    def load_data(self, directory_path=None):
        if directory_path is None:
            directory_path = self.predefined_directory_path
        if directory_path is None:
            return {"error": "No directory path provided"}, 400

        try:
            # Clear existing collection
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(self.collection_name, metadata={"hnws:space":"cosine"})
                        
            # Load and process files
            print("\nEmbedding Files")
            print("-----------------")
            
            for root, _, files in os.walk(directory_path):                        
                input_files=[]                              
                for file in files:
                    if file.endswith(".json"):
                        print("Json file detected")
                        self.process_json(file)
                    else:
                        input_files.append(os.path.join(directory_path,file))
                
                try:    
                    reader=SimpleDirectoryReader(input_files=input_files)
                except Exception as e :
                    print(e)
                    
                documents = reader.load_data()     
                for idx , doc in enumerate(tqdm(documents)):                 
                    try:
                        self.collection.add(#embeddings=self.model.encode(doc.get_text()).tolist(),
                                            metadatas=doc.metadata,
                                            ids=f"{doc.metadata["file_name"]}_{idx}",
                                            documents=doc.get_text())
                    except ValueError as v:
                        print({"error":f"Error adding {file} to collection. {v}"})
                        
            """ print(embedding)
            print(metadata)
            print(ids)
            print(content)
             """
             
            print(f"\nCollection {self.collection_name} Loaded")           
            print("-----------------")
            print(f"No. of Entries: {self.collection.count()}") 
            
                     
            return {"message": "Dataset Loaded"}
        except Exception as e:
            return {"error": f"Error loading data: {e}"}

    def retrieve_documents(self, query_str):
        try:
            similarities = self.collection.query(query_texts=query_str,
                                                 n_results=1)
                                
            print("-----------------")
            print(f"Query: '{query_str}'")
            print(similarities["documents"])
            return (similarities["documents"])
        
        except Exception as e:
            return {"error": f"Error retrieving documents: {e}"}
        
        
""" 
# Example usage
if __name__ == "__main__":
    # Initialize the DocumentRetrieval class
    doc_retrieval = Dataset(predefined_directory_path=r'G:\My Drive\Dissertation_Database')

    # Load data into the collection
    load_response = doc_retrieval.load_data()
    #print(load_response)

    # Retrieve documents based on a query
    query = "I want to start a career in engineering where should i start?"
    retrieve_response = doc_retrieval.retrieve_documents(query)
    print(retrieve_response) """

