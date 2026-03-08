from sqlalchemy import inspect
from database.db_manager import engine

def get_schema():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    schema = ""

    for table in tables:

        schema += f"\nTable: {table}\n"

        columns = inspector.get_columns(table)

        for col in columns:

            schema += f"{col['name']} ({col['type']})\n"

    return schema