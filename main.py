from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from sqlalchemy import create_engine

from squirrel import prompts
from squirrel.db import describe_db, results_as_str

ENGINE = engine = create_engine("sqlite:///chinook.db")
ENGINE_DESC = describe_db(ENGINE)


class GraphState(BaseModel):
    question: str | None = None
    valid: bool | None = None
    results: str | None = []
    response: str | None = None


def validator_node(state: GraphState) -> dict[str, str]:
    valid = prompts.question_validation_chain().invoke(
        {
            "context": ENGINE_DESC,
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
            "context": ENGINE_DESC,
            "question": state.question,
        }
    )
    results = results_as_str(sql=sql, engine=ENGINE)
    return {"results": results}


def generator_node(state: GraphState) -> dict[str, str]:
    response = prompts.rag_chain().invoke(
        {
            "context": state.results,
            "question": state.question,
        }
    )
    return {"response": response}


def main():
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

    inputs = {"question": "Where is the artist 'AC/DC' from?"}
    for event in rag_pipeline.stream(inputs, stream_mode="updates"):
        for value in event.values():
            print("Assistant:", value)


if __name__ == "__main__":
    main()
