# LLM-apps-on-rag
This is a repository to learn and demonstrate the LLM application using RAG system. As there are many variation of the RAG system, this repository aims to serve as study room of many RAG variants as possible to develop the understanding on the subject


## Elasticsearch Installation
- Below command will pull official elasticsearch image from the docker hub
```bash
docker pull elasticsearch:8.4.3
```

- create a docker network 
```bash
docker network create rag-network
```

- build & run the docker container
```bash
docker run -d --name elasticsearch-1 --net rag-network -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" -e "xpack.security.http.ssl.enabled=false" docker.elastic.co/elasticsearch/elasticsearch:8.12.1
```

## Python library installation

- run the below command in the projects root directory

```python
pip install -r requirements.txt
```