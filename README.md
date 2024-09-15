# LLM-apps-on-rag
This is a repository to learn &amp; demonstrate the LLM application using RAG system. As there are many variation of the RAG system, this repository aims to serve as study room of many RAG variants as possible to develop the understanding on the subject


## Elastcisearch Intsallation

```bash
docker pull elasticsearch:8.4.3
```

```bash
docker network create rag-network
```

```bash
docker run -d --name elasticsearch-1 --net rag-network -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:8.4.3
```

### Python Libraries Installation

```bash
python -m pip install -q requirements.txt
```