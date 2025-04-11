from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

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

llm_engine = ChatGoogleGenerativeAI()
rag_chain = rag_prompt | llm_engine | StrOutputParser()
