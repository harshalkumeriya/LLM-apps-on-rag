from elasticsearch import Elasticsearch


index_name = "mf-faq"
es_client = Elasticsearch([{'host': 'localhost', 'port': 9200}])
print(es_client.info())


# # Example query: Search for documents where the question contains 'KYC'
# search_query = {
#     "size": 2,
#     "query": {
#         "match": {
#             "question": "KYC"
#         }
#     }
# }

# Example query: Search for documents where the question contains 'debt mutual fund'
user_query = "what is debt mutual fund?"
search_query = {
    "size": 2,
    "query": {
        "match": {
            "question": user_query
        }
    }
}


# Perform the search
response = es_client.search(index=index_name, body=search_query)

# Print the results
for hit in response['hits']['hits']:
    print(f"ID: {hit['_id']}")
    print(f"Section: {hit['_source']['section']}")
    print(f"Question: {hit['_source']['question']}")
    print(f"Answer: {hit['_source']['answer']}")
    print(f"Link: {hit['_source']['link']}")
    print("-" * 80)
