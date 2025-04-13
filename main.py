from sqlalchemy import create_engine

from squirrel.dag import answer_question

if __name__ == "__main__":
    engine = create_engine("sqlite:///chinook.db")
    print(answer_question("Where is the artist 'AC/DC' from?", engine))
