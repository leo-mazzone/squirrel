from typing import Any

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from sqlalchemy import Engine

from squirrel import prompts
from squirrel.db import describe_db, results_as_str


class GraphState(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    engine: Engine | None = None
    question: str | None = None
    valid: bool | None = None
    sql: str | None = None
    results: str | None = ""
    response: str | None = None


def validator_node(state: GraphState) -> dict[str, str]:
    valid = prompts.question_validation_chain().invoke(
        {
            "context": describe_db(state.engine),
            "question": state.question,
        }
    )
    return {"valid": valid}


def retriever_backstop(state: GraphState) -> str:
    if state.valid:
        return "retriever_node"
    return "refusal_node"


def refusal_node(state: GraphState) -> dict[str, str]:
    return {"response": "I cannot answer that question."}


def retriever_node(state: GraphState) -> dict[str, str]:
    sql = prompts.sql_chain().invoke(
        {
            "context": describe_db(state.engine),
            "question": state.question,
        }
    )
    results = results_as_str(sql=str(sql), engine=state.engine)
    return {"results": results, "sql": sql}


def generator_node(state: GraphState) -> dict[str, str]:
    response = prompts.rag_chain().invoke(
        {
            "context": state.results,
            "question": state.question,
        }
    )
    return {"response": response}


def ask(question: str, engine: Engine) -> tuple[str, list[dict[str, Any]]]:
    pipeline = StateGraph(GraphState)

    pipeline.add_node("validator_node", validator_node)
    pipeline.add_node("retriever_node", retriever_node)
    pipeline.add_node("generator_node", generator_node)
    pipeline.add_node("refusal_node", refusal_node)

    pipeline.add_edge(START, "validator_node")
    pipeline.add_conditional_edges("validator_node", retriever_backstop)
    pipeline.add_edge("retriever_node", "generator_node")
    pipeline.add_edge("refusal_node", END)
    pipeline.add_edge("generator_node", END)

    rag_pipeline = pipeline.compile()

    inputs = {"question": question, "engine": engine}
    state_history = []
    for event in rag_pipeline.stream(inputs, stream_mode="debug"):
        state_history.append(event)

    answer = dict(state_history[-1]["payload"]["result"])["response"]

    return answer, state_history
