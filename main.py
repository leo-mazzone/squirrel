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


def validator_node(state: GraphState) -> dict[str, str]:
    state.valid = prompts.question_validation_chain().invoke(
        {
            "context": ENGINE_DESC,
            "question": state.question,
        }
    )
    return {"valid": state.valid}


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
    generation = prompts.rag_chain().invoke(
        {
            "context": state.results,
            "question": state.question,
        }
    )
    return {"generation": generation}


def main():
    print(describe_db(ENGINE))


if __name__ == "__main__":
    main()
