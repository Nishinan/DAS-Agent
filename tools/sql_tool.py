from database.db_manager import execute_sql

def run_sql(query):

    try:

        result = execute_sql(query)

        return result[:20]

    except Exception as e:

        return f"SQL Error: {str(e)}"
        