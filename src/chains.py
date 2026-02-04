import os
import logging
import getpass

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from langchain_google_genai import ChatGoogleGenerativeAI

from pydantic import BaseModel, Field
from typing import List, Dict

from src.model import CosyChatOllama

from dotenv import load_dotenv

load_dotenv()

def read_markdown_file(name: str) -> str:
    file_path =    name
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"The file {file_path} does not exist.")
        return ""
    except IOError:
        print(f"An error occurred while reading the file {file_path}.")
        return ""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models for parsers
class QuestionModel(BaseModel):
    questions: List[str] = Field(description='list of generated natural language questions')

class PairsModel(BaseModel):
    questions: List[Dict] = Field(description='list of generated natural language questions - Cypher query pairs')

class CypherDecModel(BaseModel):
    cypher_tool: str = Field(description="decides which cypher prompt to use")


class CypherModel(BaseModel):
    cypher_query: str = Field(description="cypher query")

class AssessModel(BaseModel):
    output: str = Field(description="Binary result showing if the query makes biological sense")


# Generator chain
def create_question_generator_chain():

    # prompt
    chain_instructions = read_markdown_file(os.path.join('prompts', 'NL_chain_instructions.md'))
    chain_prompt = read_markdown_file(os.path.join('prompts', 'NL_chain_prompt.md'))
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", chain_instructions),
            ("human", chain_prompt)
        ]
    )

    # llm
    llm = CosyChatOllama(model = 'mistral:7b', temperature= 1.0, num_ctx = 2500)

    # parser
    parser = PydanticOutputParser(pydantic_object=QuestionModel)

    generator_chain = prompt | llm | parser
    return generator_chain


if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")


def create_advanced_question_generator_chain():
    # prompt
    chain_instructions = read_markdown_file(os.path.join('prompts', 'NL_chain_instructions.md'))
    chain_prompt = read_markdown_file(os.path.join('prompts', 'NL_chain_prompt.md'))
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", chain_instructions),
            ("human", chain_prompt)
        ]
    )

    # llm
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 1.0)

    # parser
    parser = PydanticOutputParser(pydantic_object=QuestionModel)

    generator_chain = prompt | llm | parser
    return generator_chain


# Translator chain
def create_translator_chain(model_name= 'qwen2.5-coder:latest'):

    # prompt
    chain_instructions = read_markdown_file(os.path.join('prompts','translator_chain_instructions.md'))
    chain_prompt = read_markdown_file(os.path.join('prompts','translator_chain_prompt.md'))
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", chain_instructions),
            ("human", chain_prompt)
        ]
    )

    # llm (coder expert)
    coder_llm = CosyChatOllama(model= model_name, num_ctx = 25000)
    # parser
    parser = PydanticOutputParser(pydantic_object=PairsModel)


    translator_chain = prompt | coder_llm | parser
    return translator_chain

