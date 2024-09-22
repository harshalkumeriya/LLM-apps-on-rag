from tqdm.auto import tqdm

from helpers import (
    ElasticsearchHandler, 
    EmbeddingGenerator,
    DocumentLoader, 
    VectorConfig
)


class DocumentIndexer:
    def __init__(self, config):
        self.config = config
        self.document_loader = DocumentLoader()
        self.embedding_generator = EmbeddingGenerator(config.embedding_model)
        self.es_handler = ElasticsearchHandler(config.es_host)

    def index_documents(self, index_settings):
        # Step 1: Load documents
        documents = self.document_loader.load_documents(self.config.filename)
        if len(documents) > 0:
            # Step 2: Create embeddings
            embeded_documents = self.embedding_generator.generate_embeddings(documents)
            # Step 3: Create mapping & index
            self.es_handler.create_index(self.config.index_name, index_settings)
            # Step 4: Add documents to index
            self.es_handler.index_documents(self.config.index_name, embeded_documents)
        else:
            raise Exception("documents are empty.")

    def search_documents(self, search_term, k=5, candidates=50):
        vector_search_term = self.embedding_generator.model.encode(search_term)
        query = {
            "field": "text_encoding",
            "query_vector": vector_search_term,
            "k": k,
            "num_candidates": candidates,
        }
        return self.es_handler.vector_search(self.config.index_name, query)


if __name__ == "__main__":
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
    indexer = DocumentIndexer(VectorConfig)
    indexer.index_documents(index_settings)
    search_results = indexer.search_documents("what is debt mutual fund?", k=2)
    for hit in search_results['hits']['hits']:
        print(f"ID: {hit['_id']}")
        print(f"\nSection:\n {hit['_source']['section']}")
        print(f"\nQuestion:\n {hit['_source']['question']}")
        print(f"\nAnswer:\n {hit['_source']['answer']}")
        print(f"\nLink:\n {hit['_source']['link']}")
        print("-" * 80)