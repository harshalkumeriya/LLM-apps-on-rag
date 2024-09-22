class Config:
    FILENAME = './data/outputs/mutual_fund_faq.json'
    INDEX_NAME = "mf-faq-std"
    ES_HOST = "http://localhost:9200"


# Define a configuration class for reusable settings
class VectorConfig:
    filename = './data/outputs/mutual_fund_faq.json'
    index_name = "mf-faq"
    embedding_model = "all-mpnet-base-v2"
    es_host = "http://localhost:9200"