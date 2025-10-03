from os import getenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from pydantic import SecretStr

from squirrel.utils import clean_markdown_code_blocks


class CleaningStrOutputParser(StrOutputParser):
    """String output parser that also cleans markdown code blocks."""

    def parse(self, text: str) -> str:
        """Parse the output and clean markdown code blocks."""
        return clean_markdown_code_blocks(text)


API_KEY = getenv("GEMINI_API_KEY")

llm_engine = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash", api_key=SecretStr(API_KEY) if API_KEY else None
)


def question_validation_chain() -> Runnable:
    system_prompt = """
    As context, you are given a JSON description of all the tables available in a
    SQLite database, and a user question. You need to determine if the user question can
    be answered exclusively using data from the database. If the user question cannot be
    answered from the database, or if the question is not about data, just return the
    word False, otherwise return ONLY the word True.
    """

    human_prompt = """
    Question: {question}

    Database structure: 
    {context}

    Answer:
    """

    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
    )

    return rag_prompt | llm_engine | CleaningStrOutputParser()


def sql_chain() -> Runnable:
    system_prompt = """
    You are an assistant for question-answering tasks. As context, you are given a
    JSON description of all the tables available in a SQLite database. From the user's
    question, generate a valid SQL query for this database that will retrieve data
    relevant to answer the user question. 

    CRITICAL: Only provide the raw, unformatted SQL query and nothing else! 
    - Do NOT use markdown code blocks (```sql)
    - Do NOT include any explanatory text
    - Do NOT include any formatting
    - Your output should start with the word "SELECT" 
    - End your output immediately after the query

    When working with date queries:
    - Look for date/datetime columns in the database schema
    - Use proper SQL date comparison operators (BETWEEN, >=, <=, =)
    - For date ranges, use BETWEEN 'start_date' AND 'end_date' 
    - For date strings, use standard ISO format 'YYYY-MM-DD'
    - Handle both DATE and DATETIME column types appropriately
    - If the question mentions specific date ranges, incorporate them into WHERE clauses
    """

    human_prompt = """
    Question: {question}

    Database structure: 
    {context}

    Answer:
    """

    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
    )

    return rag_prompt | llm_engine | CleaningStrOutputParser()


def rag_chain() -> Runnable:
    system_prompt = """
    You are an assistant for question-answering tasks. As context, use the following
    results from a SQL database query, retrieved to answer the question. If you don't
    know the answer, just say that you don't know. Use one or two sentences maximum and
    keep the answer concise. Only provide the answer and nothing else!
    """

    human_prompt = """
    Question: {question}

    Context: 
    {context}

    Answer:
    """

    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
    )

    return rag_prompt | llm_engine | CleaningStrOutputParser()
