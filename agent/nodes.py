from agent.state import AgentState
from utils.llm import get_router_llm, get_main_llm
from tools.schema_tool import get_schema
from tools.sql_tool import run_sql

router_llm = get_router_llm()
main_llm = get_main_llm()


def intent_node(state: AgentState):

    question = state["question"]

    prompt = f"""
Classify the user request.

Categories:
data_analysis
general_question

Question:
{question}

Return only category.
"""

    result = router_llm.invoke(prompt)

    state["intent"] = result.content.strip()

    return state


def schema_node(state: AgentState):

    schema = get_schema()

    state["schema"] = schema

    return state


def sql_node(state: AgentState):

    question = state["question"]

    schema = state["schema"]

    prompt = f"""
You are a SQL expert.

Database schema:
{schema}

Generate SQL to answer:
{question}

Return SQL only.
"""

    sql = main_llm.invoke(prompt)

    query = sql.content.strip()

    result = run_sql(query)

    state["sql_query"] = query
    state["query_result"] = result

    return state


def insight_node(state: AgentState):

    question = state["question"]
    result = state["query_result"]

    prompt = f"""
User question:
{question}

Query result:
{result}

Explain insights.
"""

    answer = main_llm.invoke(prompt)

    state["response"] = answer.content

    return state