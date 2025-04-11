from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

llm_engine = ChatGoogleGenerativeAI()


def question_validation_chain() -> ChatPromptTemplate:
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

    return rag_prompt | llm_engine | StrOutputParser()


def sql_chain() -> ChatPromptTemplate:
    system_prompt = """
    You are an assistant for question-answering tasks. As context, you are given a
    JSON description of all the tables available in a SQLite database. From the user's
    question, generate a valid SQL query for this database that will retrieve data
    relevant to answer the user question. If the user question cannot be answered from
    the database, or if the question is not about data, just say that you can't answer.
    Only provide the SQL query and nothing else!
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

    return rag_prompt | llm_engine | StrOutputParser()


def rag_chain() -> ChatPromptTemplate:
    system_prompt = """
    You are an assistant for question-answering tasks. As context, use the following results
    from a SQL database query, retrieved to answer the question. If you don't know the
    answer, just say that you don't know. Use three sentences maximum and keep the answer
    concise. Only provide the answer and nothing else!
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

    return rag_prompt | llm_engine | StrOutputParser()
