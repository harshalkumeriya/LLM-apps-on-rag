import os

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from helpers import (
    ElasticsearchHandler, 
    EmbeddingGenerator,
    DocumentLoader, 
    VectorConfig
)

# Disable tokenizers parallelism to avoid the warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv() # OR os.environ["OPENAI_API_KEY"] = <your-token-key>


class DocumentIndexer:
    """this class convert text to vector embedding, create vector index in elastcisearch 
    and store documents in the elasticsearch document store.
    """
    def __init__(self, config: VectorConfig):
        self.config = config
        self.document_loader = DocumentLoader()
        self.embedding_generator = EmbeddingGenerator(config.embedding_model)
        self.es_handler = ElasticsearchHandler(config.es_host)

    def index_documents(self, index_settings: dict):
        # Step 1: Load documents
        documents = self.document_loader.load_documents(self.config.filename)
        if len(documents) > 0:
            # Step 2: Create embeddings
            embeded_documents = self.embedding_generator.generate_embeddings(documents)
            # Step 3: Create mapping & index
            self.es_handler.create_index(self.config.index_name, index_settings)
            # Step 4: Add documents to index
            self.es_handler.index_documents(self.config.index_name, embeded_documents)
            return 
        else:
            raise Exception("documents are empty.") 

    def search_documents(self, search_term:str, k:int=5, candidates:int=50):
        vector_search_term = self.embedding_generator.model.encode(search_term)
        query = {
            "field": "text_encoding",
            "query_vector": vector_search_term,
            "k": k,
            "num_candidates": candidates,
        }
        return self.es_handler.vector_search(self.config.index_name, query)


# Function to generate the final response using LangChain
def generate_rag_response(llm, query: str, top_k: int = 5):
    # Search for relevant context in Elasticsearch
    indexer = DocumentIndexer(VectorConfig)
    search_results = indexer.search_documents(query, k=top_k)
    # Extract the top answers
    context = ""
    for hit in search_results['hits']['hits']:
        context += f"\n\nQuestion: {hit['_source']['question']}"
        context += f"\n\nAnswer: {hit['_source']['answer']}"
        context += f"\n\nLink: {hit['_source']['link']}\n"
        context += "-" * 80
    
    system_prompt = """
    INSTRUCTIONS: In the CONTEXT, make sure to properly check spelling mistakes, observed concatenated words, remove any speacial characters.
    DO NOT answer the question based on your knowledge. Use the CONTEXT to generate the RESPONSE and if CONTEXT does not have enough information
    to answer user query, just say, 'I cannot answer this query'. Try to provide summary in the bullet points.
    Answer the question/query based on the following context:
    \nCONTEXT: {query_context}
    \nQUERY: {query}
    \nRESPONSE:
    """
    
    # Construct the prompt template for LangChain
    prompt_template = PromptTemplate(
        input_variables=["query", "context"],
        template=system_prompt
    )
    
    # Generate the final response using the retrieved context
    prompt = prompt_template.format(query=query, query_context=context)
    response = llm.invoke(prompt)
    return response

if __name__ == "__main__":
    # Initialize LangChain with an OpenAI LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=os.environ["OPENAI_API_KEY"])
    query = "what is mutual fund?"
    response = generate_rag_response(llm, query, top_k=5)
    print(response.content)