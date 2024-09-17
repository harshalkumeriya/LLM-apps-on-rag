import json
from elasticsearch import Elasticsearch
from tqdm.auto import tqdm

class Config:
    FILENAME = '/data/mutual_fund_faq.json'
    INDEX_NAME = "mf-faq"
    ES_HOST = "http://localhost:9200"
    

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


class ElasticsearchHandler:
    def __init__(self, host: str):
        self.client = Elasticsearch(host)
        print(self.client.info())

    def create_index(self, index_name: str, index_settings: dict):
        self.client.indices.delete(index=index_name, ignore_unavailable=True)
        self.client.indices.create(index=index_name, body=index_settings)
        print(f"Index {index_name} created.")

    def index_documents(self, index_name: str, documents: list):
        for doc in tqdm(documents, desc="Indexing documents"):
            self.client.index(index=index_name, document=doc)


class DocumentIndexer:
    def __init__(self, config: Config):
        self.config = config
        self.document_loader = DocumentLoader()
        self.es_handler = ElasticsearchHandler(config.ES_HOST)

    def run_indexing(self):
        # Load documents
        documents = self.document_loader.load_documents(self.config.FILENAME)
        
        # Elasticsearch index settings
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
                    "link": {"type": "keyword"}
                }
            }
        }

        # Create Elasticsearch index
        self.es_handler.create_index(self.config.INDEX_NAME, index_settings)

        # Index documents
        self.es_handler.index_documents(self.config.INDEX_NAME, documents)


if __name__ == "__main__":
    indexer = DocumentIndexer(Config)
    indexer.run_indexing()