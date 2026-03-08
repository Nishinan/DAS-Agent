from sqlalchemy import create_engine
import pandas as pd
from config import DATABASE_URI

engine = create_engine(DATABASE_URI)

def load_csv(file_path):

    df = pd.read_csv(file_path)

    df.to_sql("dataset", engine, if_exists="replace", index=False)

    return df.head()


def execute_sql(query):

    with engine.connect() as conn:

        result = conn.execute(query)

        rows = result.fetchall()

    return rows