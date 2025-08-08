from sqlalchemy import create_engine

from squirrel.dag import ask


def test_example():
    engine = create_engine("sqlite:///chinook.db")
    response, _ = ask("What is the total number of genres in the dataset?", engine)
    assert "25" in response
