import json

import polars as pl
from sqlalchemy import Engine, inspect


def describe_db(engine: Engine) -> str:
    inspector = inspect(engine)
    tables_info = {}
    table_names = inspector.get_table_names()
    print(table_names)
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


def results_as_str(query: str, engine: Engine) -> str:
    df = pl.read_database(query=query, connection=engine)
    return str(df)
