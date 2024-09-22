from helpers.common import (
    DocumentLoader,
    ElasticsearchHandler,
    Config
)

class DocumentIndexer:
    def __init__(self, config: Config, document_loader: DocumentLoader, es_handler: ElasticsearchHandler):
        self.config = config
        self.document_loader = document_loader
        self.es_handler = es_handler

    def run_indexing(self, index_settings):
        # Load documents
        documents = self.document_loader.load_documents(self.config.FILENAME)
        # Create Elasticsearch index
        self.es_handler.create_index(self.config.INDEX_NAME, index_settings)
        # Index documents
        self.es_handler.index_documents(self.config.INDEX_NAME, documents)


if __name__ == "__main__":
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
    config = Config()
    es_handler = ElasticsearchHandler(host=config.ES_HOST)
    document_loader = DocumentLoader()

    # run indexing
    indexer = DocumentIndexer(config, document_loader, es_handler)
    indexer.run_indexing(index_settings)