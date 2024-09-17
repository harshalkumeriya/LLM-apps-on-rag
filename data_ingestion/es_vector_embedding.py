import json

from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from tqdm.auto import tqdm

# Define a configuration class for reusable settings
class Config:
    filename = '/data/mutual_fund_faq.json'
    index_name = "mf-faq"
    embedding_model = "all-mpnet-base-v2"
    es_host = "http://localhost:9200"


# DocumentLoader class handles loading documents from a file
class DocumentLoader:
    @staticmethod
    def load_documents(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                documents = json.load(file)
            print("Data has been successfully loaded from", filename)
            return documents
        except FileNotFoundError:
            print(f"The file {filename} does not exist.")
        except json.JSONDecodeError:
            print(f"Error decoding JSON from the file {filename}.")
        return []


# EmbeddingGenerator class handles the generation of embeddings
class EmbeddingGenerator:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def generate_embeddings(self, documents):
        embeded_documents = []
        for doc in documents:
            doc["text_vector"] = self.model.encode(doc["text"]).tolist()
            embeded_documents.append(doc)
        return embeded_documents


# ElasticsearchHandler class manages Elasticsearch interactions
class ElasticsearchHandler:
    def __init__(self, host):
        self.client = Elasticsearch(host)
        print(self.client.info())

    def create_index(self, index_name, index_settings):
        self.client.indices.delete(index=index_name, ignore_unavailable=True)
        self.client.indices.create(index=index_name, body=index_settings)

    def index_documents(self, index_name, documents):
        for doc in tqdm(documents):
            try:
                self.client.index(index=index_name, document=doc)
            except Exception as err:
                print(err)

    def search(self, index_name, query):
        return self.client.search(
            index=index_name, 
            knn=query,
            source=["text", "section", "question", "answer"]
        )


# Facade class to simplify the interaction
class DocumentIndexer:
    def __init__(self, config):
        self.config = config
        self.document_loader = DocumentLoader()
        self.embedding_generator = EmbeddingGenerator(config.embedding_model)
        self.es_handler = ElasticsearchHandler(config.es_host)

    def index_documents(self):
        # Step 1: Load documents
        documents = self.document_loader.load_documents(self.config.filename)

        # Step 2: Create embeddings
        embeded_documents = self.embedding_generator.generate_embeddings(documents)

        # Step 3: Create mapping & index
        index_settings = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0
            },
            "mappings": {
                "properties": {
                    "section": {"type": "keyword"},
                    "question": {"type": "text"},
                    "answer": {"type": "text"},
                    "link": {"type": "keyword"},
                    "text_encoding": {
                        "type": "dense_vector",
                        "dims": 768,
                        "index": True,
                        "similarity": "cosine"
                    },
                }
            }
        }
        self.es_handler.create_index(self.config.index_name, index_settings)

        # Step 4: Add documents to index
        self.es_handler.index_documents(self.config.index_name, embeded_documents)

    def search_documents(self, search_term, k=5, candidates=50):
        vector_search_term = self.embedding_generator.model.encode(search_term)
        query = {
            "field": "text_encoding",
            "query_vector": vector_search_term,
            "k": k,
            "num_candidates": candidates,
        }
        return self.es_handler.search(self.config.index_name, query)


if __name__ == "__main__":
    indexer = DocumentIndexer(Config)
    indexer.index_documents()
    search_results = indexer.search_documents("what is debt mutual fund?")
    print(search_results["hits"]["hits"])