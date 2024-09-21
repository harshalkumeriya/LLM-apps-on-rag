# https://python.langchain.com/docs/integrations/vectorstores/elasticsearch/
# https://python.langchain.com/api_reference/huggingface/embeddings/langchain_huggingface.embeddings.huggingface.HuggingFaceEmbeddings.html#

from langchain_elasticsearch import ElasticsearchStore
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2") 
# embeddings = HuggingFaceEmbeddings(model="all-mpnet-base-v2") 
vector_store = ElasticsearchStore(
    index_name = "mf-faq", 
    embedding=embeddings, 
    es_url="http://localhost:9200"
)

# Add documents
results = vector_store.similarity_search(
    query="what is debt mutual fund?",
    k=2
)
for res in results:
    print(f"* {res.page_content}")