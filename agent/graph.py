from langgraph.graph import StateGraph, END

from agent.state import AgentState
from agent.nodes import intent_node, schema_node, sql_node, insight_node
from agent.router import route


def build_graph():

    graph = StateGraph(AgentState)

    graph.add_node("intent", intent_node)

    graph.add_node("schema", schema_node)

    graph.add_node("sql", sql_node)

    graph.add_node("insight", insight_node)

    graph.set_entry_point("intent")

    graph.add_conditional_edges(
        "intent",
        route,
        {
            "schema": "schema",
            "insight": "insight"
        }
    )

    graph.add_edge("schema", "sql")

    graph.add_edge("sql", "insight")

    graph.add_edge("insight", END)

    return graph.compile()