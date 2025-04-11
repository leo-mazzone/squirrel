import json

from sqlalchemy import Engine, create_engine, inspect


def describe_db(engine: Engine) -> str:
    inspector = inspect(engine)
    tables_info = {}
    table_names = inspector.get_table_names()

    for table_name in table_names:
        columns = inspector.get_columns(table_name)

        column_info = [
            {
                "name": column["name"],
                "type": str(column["type"]),
            }
            for column in columns
        ]

        tables_info[table_name] = column_info

    return json.dumps(tables_info, indent=4)


def main():
    engine = create_engine("sqlite:///chinook.db")
    print(describe_db(engine))


if __name__ == "__main__":
    main()
