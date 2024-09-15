# 1. create vector embedding
# 2. create vector index in elastic search

from elasticsearch import Elasticsearch
import json


# Specify the filename
filename = '/data/mutual_fund_faq.json'

try:
    with open(filename, 'r', encoding='utf-8') as file:
        documents = json.load(file)
    print("Data has been successfully loaded from", filename)
except FileNotFoundError:
    print(f"The file {filename} does not exist.")
except json.JSONDecodeError:
    print(f"Error decoding JSON from the file {filename}.")
except IOError as e:
    print(f"An error occurred: {e}")


es_client = Elasticsearch("http://localhost:9200")
print(es_client.info())

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

index_name = "mf-faq"
es_client.indices.create(index=index_name, body=index_settings)

from tqdm.auto import tqdm
for doc in tqdm(documents):
    es_client.index(index=index_name, document=doc)