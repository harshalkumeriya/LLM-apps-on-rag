from helpers.common import Config, ElasticsearchHandler


# # Example query: Search for documents where the question contains 'KYC'
search_query = {
    "size": 2,
    "query": {
        "match": {
            "question": "KYC"
        }
    }
}

# Example query: Search for documents where the question contains 'debt mutual fund'
# user_query = "what is mutual fund?"
# search_query = {
#     "size": 1,
#     "query": {
#         "match": {
#             "question": user_query
#         }
#     }
# }

es_handler = ElasticsearchHandler(host=Config.ES_HOST)
response = es_handler.search(
    query=search_query, 
    index=Config.INDEX_NAME
)
for hit in response['hits']['hits']:
    print(f"ID: {hit['_id']}")
    print(f"\nSection:\n {hit['_source']['section']}")
    print(f"\nQuestion:\n {hit['_source']['question']}")
    print(f"\nAnswer:\n {hit['_source']['answer']}")
    print(f"\nLink:\n {hit['_source']['link']}")
    print("-" * 80)