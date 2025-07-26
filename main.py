from sqlalchemy import create_engine

from squirrel.dag import ask

if __name__ == "__main__":
    engine = create_engine("sqlite:///chinook.db")
    response, debug = ask("What is the total number of genres in the dataset?", engine)

    print("Response:", response)

    print("\n\n-- DEBUG --")
    retriever_node = [
        d
        for d in debug
        if d["payload"]["name"] == "retriever_node" and d["type"] == "task_result"
    ][0]

    retriever_output = dict(retriever_node["payload"]["result"])
    print("Generated SQL:\n", retriever_output["sql"])

    print("Retrieved data:\n", retriever_output["results"])
