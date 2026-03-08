from langchain_openai import ChatOpenAI
from config import MODEL_MAIN, MODEL_ROUTER

def get_main_llm():

    return ChatOpenAI(
        model=MODEL_MAIN,
        temperature=0
    )


def get_router_llm():

    return ChatOpenAI(
        model=MODEL_ROUTER,
        temperature=0
    )