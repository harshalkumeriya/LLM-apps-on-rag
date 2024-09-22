import os
import json
import dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field

# Load environment variables
dotenv.load_dotenv()

class QA(BaseModel):
    question: str = Field(description="Question from the PDF")
    answer: str = Field(description="Answer corresponding to the question from PDF")


class PDFContentExtractor:
    @staticmethod
    def extract_content(pdf_path: str) -> str:
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        return " ".join(doc.page_content for doc in documents)


class QuestionAnswerGenerator:
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

    def generate_qa_pairs(self, text: str, parser: JsonOutputParser) -> list[QA]:
        qa_pairs = []
        chunks = self._split_text(text)

        for chunk in chunks:
            response = self._generate_response(chunk, parser)
            qa_pairs.append(response)

        return qa_pairs

    def _split_text(self, text: str) -> list[str]:
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=200,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        return text_splitter.split_text(text)

    def _generate_response(self, chunk: str, parser: JsonOutputParser) -> QA:
        prompt_template = """
            You are provided with the following text from a PDF document:
            \n{chunk}

            Based on the information in the text, create relevant and concise questions.
            Then provide the corresponding answers. Make sure the questions are directly 
            related to the content and answers should be accurate based on the text.
            Format the output as a list of Question and Answer pairs.\n{format_instructions}
        """

        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["chunk"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        chain = prompt | self.llm | parser
        return chain.invoke({"chunk": chunk})


class JSONSaver:
    @staticmethod
    def save_to_json(data: list[QA], output_file: str) -> None:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Question and answer dataset saved to {output_file}")


def create_qa_dataset(pdf_path: str, output_file: str, parser: JsonOutputParser, openai_api_key: str) -> None:
    # Step 1: Extract content from PDF
    text = PDFContentExtractor.extract_content(pdf_path)

    # Step 2: Generate questions and answers
    qa_generator = QuestionAnswerGenerator(api_key=openai_api_key)
    qa_pairs = qa_generator.generate_qa_pairs(text, parser)

    # Step 3: Save the questions and answers to JSON
    JSONSaver.save_to_json(qa_pairs, output_file)

if __name__ == "__main__":
    # Provide the path to your PDF and the OpenAI API key
    pdf_path = "../data/inputs/Master Circular for Mutual Funds.pdf"
    output_file = "../data/outputs/mf_master_circular_qa.json"
    openai_api_key = os.environ["OPENAI_API_KEY"]
    
    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=QA)
    
    # Call the function to create the QA dataset
    create_qa_dataset(pdf_path, output_file, parser, openai_api_key)