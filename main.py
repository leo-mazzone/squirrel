from pydantic import BaseModel
from sqlalchemy import create_engine

from squirrel.db import describe_db, results_as_str

ENGINE = engine = create_engine("sqlite:///chinook.db")


class GraphState(BaseModel):
    question: str | None = None
    db_description: str | None = None
    results: str | None = []


def retriever_node(state: GraphState) -> dict[str, str]:
    state.results = results_as_str(sql=state.sql, engine=ENGINE)
    return {"results": state.results}


def main():
    print(describe_db(ENGINE))


if __name__ == "__main__":
    main()
