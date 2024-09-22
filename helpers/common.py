from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm
import json


# DocumentLoader class handles loading documents from a fi
class DocumentLoader:
    @staticmethod
    def load_documents(filename: str):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                documents = json.load(file)
            print("Data has been successfully loaded from", filename)
            return documents
        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
            return []
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the file {filename}.")
            return []
        except IOError as e:
            print(f"An error occurred: {e}")
            return []


# EmbeddingGenerator class handles the generation of embeddings
class EmbeddingGenerator:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, documents):
        embeded_documents = []
        for doc in documents:
            doc["text_encoding"] = self.model.encode(doc["answer"]).tolist()
            embeded_documents.append(doc)
        return embeded_documents
    
    def encode(self, text):
        return self.model.encode(text)


class ElasticsearchHandler:
    def __init__(self, host: str):
        self.client = Elasticsearch(host)

    def create_index(self, index_name: str, index_settings: dict) -> None:
        try:
            self.client.indices.delete(index=index_name)
            print(f"found index {index_name}. \n deleted index {index_name}")
        except:
            self.client.indices.delete(index=index_name, ignore_unavailable=True)
        finally:
            self.client.indices.create(index=index_name, body=index_settings)
            print(f"Index {index_name} created.")
        return

    def index_documents(self, index_name: str, documents: list):
        for doc in tqdm(documents, desc="Indexing documents"):
            try:
                self.client.index(index=index_name, document=doc)
            except Exception as err:
                raise err

    def search(self, query, index):
        print(f"searching index: {index} \n query: {query}")
        return self.client.search(index=index, body=query)

    def vector_search(self, index_name, query):
        return self.client.search(
            index=index_name, 
            knn=query,
            source=["section", "question", "answer", "link"]
        )