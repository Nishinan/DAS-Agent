from typing import TypedDict, List, Any

class AgentState(TypedDict):

    question: str
    intent: str

    schema: str

    sql_query: str
    query_result: Any

    response: str