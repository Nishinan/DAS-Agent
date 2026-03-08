from fastapi import FastAPI, UploadFile, File
import shutil

from agent.graph import build_graph
from database.db_manager import load_csv

app = FastAPI()

agent = build_graph()


@app.post("/upload")

async def upload_dataset(file: UploadFile = File(...)):

    path = f"temp_{file.filename}"

    with open(path, "wb") as buffer:

        shutil.copyfileobj(file.file, buffer)

    preview = load_csv(path)

    return {"preview": str(preview)}


@app.post("/chat")

async def chat(question: str):

    state = {

        "question": question,

        "intent": "",

        "schema": "",

        "sql_query": "",

        "query_result": "",

        "response": ""
    }

    result = agent.invoke(state)

    return result