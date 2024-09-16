# Install necessary libraries
import os
import json

import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

dotenv.load_dotenv()

# Define your desired data structure.
class QA(BaseModel):
    question: str = Field(description="question from the PDF")
    answer: str = Field(description="answer corresponding to question from PDF")

# Function to extract content from PDF using langchain's PyPDFLoader
def extract_pdf_content(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    text = " ".join([doc.page_content for doc in documents])
    return text

# Function to generate questions and answers using OpenAI LLM
def generate_questions_answers(text, parser, openai_api_key):
    qa_pairs = []

    # Initialize OpenAI with your API key
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)

    # Split the content into smaller chunks for better LLM processing
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=200,
        chunk_overlap=20,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_text(text)

    # Define the prompt template for generating questions and answers
    prompt_template = """
        You are provided with the following text from a PDF document:
        \n{chunk}

        Based on the information in the text, create relevant and concise questions.
        Then provide the corresponding answers. Make sure the questions are directly 
        related to the content and answers should be accurate based on the text.
        Format the output as a list of Question and Answer pairs.\n{format_instructions}
    """

    for chunk in chunks:
        # Fill in the template with the chunk text
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["chunk"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        # Generate the question and answer pairs using the LLM
        chain = prompt | llm | parser

        response = chain.invoke({"chunk": chunk})
        
        # Process the response and store in a dictionary
        qa_pairs.append(response)

    return qa_pairs

# Function to save the questions and answers in JSON format
def save_to_json(qa_pairs, output_file):
    with open(output_file, "w") as f:
        json.dump(qa_pairs, f, indent=4)

# Main function to run the pipeline
def create_qa_dataset(pdf_path, output_file, parser, openai_api_key):
    # Step 1: Extract content from PDF
    text = extract_pdf_content(pdf_path)

    # Step 2: Generate questions and answers
    qa_pairs = generate_questions_answers(text, parser, openai_api_key)

    # Step 3: Save the questions and answers to JSON
    save_to_json(qa_pairs, output_file)
    print(f"Question and answer dataset saved to {output_file}")

if __name__ == "__main__":
    # Provide the path to your PDF and the OpenAI API key
    pdf_path = "./data/Master Circular for Mutual Funds.pdf"
    output_file = "./data/mf_master_circular_qa.json"
    openai_api_key = os.environ["OPENAI_API_KEY"]
    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=QA)
    # Call the function to create the QA dataset
    create_qa_dataset(pdf_path, output_file, parser, openai_api_key)
