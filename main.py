from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel
from sqlalchemy import create_engine

from squirrel import prompts
from squirrel.db import describe_db, results_as_str

ENGINE = engine = create_engine("sqlite:///chinook.db")
ENGINE_DESC = describe_db(ENGINE)


class GraphState(BaseModel):
    question: str | None = None
    db_description: str | None = None
    valid: bool | None = None
    results: str | None = []
    response: str | None = None


def validator_node(state: GraphState) -> dict[str, str]:
    state.valid = prompts.question_validation_chain().invoke(
        {
            "context": ENGINE_DESC,
            "question": state.question,
        }
    )
    return state.valid


def retriever_node(state: GraphState) -> dict[str, str]:
    sql = prompts.sql_chain().invoke(
        {
            "context": ENGINE_DESC,
            "question": state.question,
        }
    )
    state.results = results_as_str(sql=sql, engine=ENGINE)
    return {"results": state.results}


def generation_node(state: GraphState) -> dict[str, str]:
    state.response = prompts.rag_chain().invoke(
        {
            "context": state.results,
            "question": state.question,
        }
    )
    return {"generation": state.response}


def main():
    pipeline = StateGraph(GraphState)

    # pipeline.add_node("validator_node", validator_node)
    pipeline.add_node("retriever_node", retriever_node)
    pipeline.add_node("generator_node", generation_node)

    # pipeline.add_edge(START, "validator_node")
    pipeline.add_conditional_edges(
        START,
        validator_node,
        {
            "False": END,
            "True": "retriever_node",
        },
    )
    pipeline.add_edge("retriever_node", "generator_node")
    pipeline.add_edge("generator_node", END)

    rag_pipeline = pipeline.compile()

    inputs = {"question": "Which artist has produced the most albums last year?"}
    outputs = rag_pipeline.stream(inputs, stream_mode="updates")


if __name__ == "__main__":
    main()
