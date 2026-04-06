import json
import asyncio
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
from utils.llm import _call_huggingface_stream
from agent.graph import build_graph
from database.db_manager import load_csv

import sys
import os
import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from config import (
    ACTIVE_MODEL_PROVIDER)
from utils.memory import sessions_history, long_term_facts

# 导入你的 Agent 逻辑
from agent.graph import build_graph

app = FastAPI()
agent = build_graph()


# --- 1. 接通文件上传接口 ---
@app.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    # 前端 app.js 触发文件上传后，会寻找此接口
    path = f"temp_{file.filename}"
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 你的原有逻辑：加载到数据库并返回预览
    preview = load_csv(path)
    return {"preview": str(preview.head())}

# # --- 2. 接通流式对话接口 (核心) ---
# @app.post("/api/chat/stream")
# async def chat_stream(request: Request):
#     # 前端发送的数据包含: session_id, mode, message
#     data = await request.json()
#     user_message = data.get("message")
    
#     # 构造 LangGraph 初始状态
#     state = {
#         "question": user_message,
#         "intent": "",
#         "schema": "",
#         "sql_query": "",
#         "query_result": "",
#         "response": ""
#     }

#     async def event_generator():
#         try:
#             # 执行 LangGraph 逻辑
#             # 注意：如果 agent.invoke 是同步的，建议用 run_in_executor
#             result = agent.invoke(state)
            
#             # 模拟流式 Token 输出（前端 app.js 行 638 期望 payload.delta）
#             # 由于当前逻辑是全量返回，我们直接发送最终回复
#             response_text = result.get("response", "未生成有效回复")
            
#             yield f"data: {json.dumps({'event': 'token', 'payload': {'delta': response_text}})}\n\n"
            
#             # 发送 Final 事件（前端 app.js 行 653 期望 payload.text）
#             yield f"data: {json.dumps({'event': 'final', 'payload': {'text': response_text}})}\n\n"
            
#         except Exception as e:
#             # 错误处理（前端 app.js 行 669 期望 payload.message）
#             yield f"data: {json.dumps({'event': 'error', 'payload': {'message': str(e)}})}\n\n"

#     return StreamingResponse(event_generator(), media_type="text/event-stream")
# 2. 直接在 main.py 定义前端需要的接口，避免导入 CS5260-main/app 报错


import asyncio
import json
from fastapi import Request
from fastapi.responses import StreamingResponse
from agent.graph import build_graph  # 确保你已经写好了 build_graph
from utils.memory import sessions_history, long_term_facts

# 编译 Graph 实例（建议放在函数外，避免重复编译）
agent_app = build_graph()

# 修改 CS5260-project/DAS-Agent/main.py
@app.post("/api/chat/stream")
async def chat_stream(request: Request):
    data = await request.json()
    user_input = data.get("message")
    session_id = data.get("session_id") or "default"
    
    # 初始状态构造
    initial_state = {
        "question": user_input,
        "session_id": session_id,
        "task_list": [],
        "current_step_index": 0,
        "messages": sessions_history.get(session_id, [])[-6:],
        "review_feedback": ""
    }

    async def event_generator():
        full_response = ""
        try:
            # 使用 LangGraph 的异步流式接口
            async for event in agent.astream(initial_state, stream_mode="updates"):
                for node_name, node_output in event.items():
                    # 向前端发送中间节点的“心跳”消息，模拟 Manus 效果
                    if node_name == "planner":
                        msg = ">>>> [SERVER] 正在规划任务步骤...\n"
                        yield f"data: {json.dumps({'event': 'token', 'payload': {'delta': msg}})}\n\n"
                    elif node_name == "executor":
                        msg = ">>>> [SERVER] 正在执行子任务...\n"
                        yield f"data: {json.dumps({'event': 'token', 'payload': {'delta': msg}})}\n\n"
                    elif node_name == "reviewer":
                        feedback = node_output.get("review_feedback", "")
                        msg = f">>>> [SERVER] 评审反馈: {feedback}\n"
                        yield f"data: {json.dumps({'event': 'token', 'payload': {'delta': msg}})}\n\n"
                    elif node_name == "summarizer":
                        # 最终答案输出
                        full_response = node_output.get("response", "")
                        yield f"data: {json.dumps({'event': 'token', 'payload': {'delta': full_response}})}\n\n"

            # 结束后同步到短期记忆
            history = sessions_history.get(session_id, [])
            history.append({"role": "user", "content": user_input})
            history.append({"role": "assistant", "content": full_response})
            sessions_history[session_id] = history[-10:]
            
            yield f"data: {json.dumps({'event': 'final', 'payload': {'text': full_response}})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'payload': {'message': str(e)}})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# --- 3. 接通会话重置接口 ---
@app.post("/api/chat/reset")
async def reset_chat(request: Request):
    # 前端删除聊天时会调用此接口
    data = await request.json()
    session_id = data.get("session_id")
    # 这里可以添加清理数据库或内存中该 session 状态的逻辑
    return {"ok": True, "cleared": True}


# # --- 关键修改：定义并挂载前端路径 ---
# # 根据你的要求：前端位于 ../CS5260-main/frontend
# current_dir = os.path.dirname(os.path.abspath(__file__))
# frontend_path = os.path.normpath(os.path.join(current_dir, "..", "CS5260-main", "frontend"))

# if os.path.exists(frontend_path):
#     # 挂载静态资源：访问 http://localhost:8000/ 会自动寻找 index.html
#     app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
#     print(f"✅ 前端已成功挂载于: {frontend_path}")
# else:
#     print(f"❌ 警告：未找到前端目录 {frontend_path}，请检查路径。")
# 3. 挂载前端 (确保在所有 API 定义之后)

# 1. 修正路径：确保 Python 能找到所有文件夹
current_dir = os.path.dirname(os.path.abspath(__file__)) # DAS_Agent 目录
project_root = os.path.dirname(current_dir)             # Projects 根目录
sys.path.append(project_root)

frontend_path = os.path.join(project_root, "Web", "frontend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
    print(f"✅ 前端已挂载: {frontend_path}")

if __name__ == "__main__":
    import uvicorn
    # 启动服务器，监听 8000 端口
    uvicorn.run(app, host="0.0.0.0", port=8000)