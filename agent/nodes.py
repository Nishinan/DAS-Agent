from utils.llm import call_llm
from agent.state import AgentState
from utils.llm import call_llm
from agent.state import AgentState

# 设置最大记忆轮数（例如保留最近 5 轮往返，即 10 条消息）
MAX_MEMORY_NOTES = 10 

import json
from utils.llm import call_llm
from agent.state import AgentState

# --- 全局内存存储（Server 存续期间有效） ---
from utils.memory import sessions_history, long_term_facts

# 这里的 MAX_MEMORY_NOTES 建议设为 6 (3轮对话)
MAX_MEMORY_NOTES = 6


import json
from agent.state import AgentState
from utils.llm import call_llm  # 使用你代码里的 call_llm
from utils.memory import long_term_facts, sessions_history # 假设你的全局变量位置
# 修改 CS5260-project/DAS-Agent/agent/nodes.py
import json
from agent.state import AgentState
from utils.llm import call_llm
from utils.memory import sessions_history, long_term_facts #

import json
from agent.state import AgentState
from utils.llm import call_llm
from utils.memory import sessions_history, long_term_facts

import json
from agent.state import AgentState
from utils.llm import call_llm
from utils.memory import sessions_history, long_term_facts

def process_llm_call(gen_or_str, node_name="NODE"):
    """兼顾流式打印与逻辑拼接的辅助函数"""
    if isinstance(gen_or_str, str):
        return gen_or_str
    
    full_text = ""
    print(f"\n>>>> [SERVER LOG] {node_name} 开始输出: ", end="", flush=True)
    try:
        for token in gen_or_str:
            full_text += token
            print(token, end="", flush=True)
        print("\n")
        return full_text
    except Exception as e:
        print(f"\n>>>> [ERROR] {node_name} 流处理异常: {e}")
        return str(gen_or_str)

def pre_processor_node(state: AgentState):
    """入口节点：处理记忆指令"""
    user_input = state["question"]
    session_id = state.get("session_id", "default")
    
    if any(keyword in user_input.lower() for keyword in ["记住", "remember"]):
        prompt = f"从以下话语中提取需要永久记忆的事实：{user_input}"
        fact = process_llm_call(call_llm(prompt), "PRE_PROCESSOR").strip()
        
        old_mem = long_term_facts.get(session_id, "")
        long_term_facts[session_id] = f"{old_mem} | {fact}".strip(" | ")
        return {"response": f"✅ 已记住：{fact}", "intent": "memory_done"}
    
    return {"intent": "task", "task_list": [], "current_step_index": 0, "review_feedback": ""}

def planner_node(state: AgentState):
    """规划器：修复语法错误并强化拆解逻辑"""
    task_list = state.get("task_list", [])
    curr_idx = state.get("current_step_index", 0)
    feedback = state.get("review_feedback", "")

    if not task_list:
        # 修复 SyntaxError: 将包含引号和转义的字符串放在外部
        json_example = '[{"task": "具体的步骤描述"}]'
        prompt = (
            f"用户需求：{state['question']}\n"
            f"你是一个行动派 Agent。请将需求拆解为具体的执行步骤，不要反问用户。\n"
            f"必须以 JSON 数组格式返回，例如：{json_example}"
        )
        
        resp = process_llm_call(call_llm(prompt), "PLANNER")
        try:
            start, end = resp.find("["), resp.rfind("]") + 1
            task_list = [{"task": t["task"], "status": "pending", "result": ""} for t in json.loads(resp[start:end])]
        except:
            task_list = [{"task": f"直接回答用户：{state['question']}", "status": "pending", "result": ""}]
    else:
        # 局部修正逻辑
        prompt = f"原任务：{task_list[curr_idx]['task']}\n评审意见：{feedback}\n请重新描述该步骤使其更具可执行性。"
        task_list[curr_idx]["task"] = process_llm_call(call_llm(prompt), "RE-PLANNER").strip()
    
    return {"task_list": task_list, "review_feedback": ""}

def executor_node(state: AgentState):
    """执行器"""
    idx = state["current_step_index"]
    task = state["task_list"][idx]["task"]
    resp = process_llm_call(call_llm(f"请直接执行此任务，不要问问题：{task}"), f"EXECUTOR-STEP-{idx+1}")
    
    new_list = list(state["task_list"])
    new_list[idx].update({"result": resp, "status": "done"})
    return {"task_list": new_list}

def reviewer_node(state: AgentState):
    """评审器：确保存入字符串"""
    idx = state["current_step_index"]
    res = state["task_list"][idx]["result"]
    prompt = f"任务结果：{res}\n结果是否正面回答了问题且逻辑达标？通过回复PASS，否则回复FAIL:原因"
    review = process_llm_call(call_llm(prompt), "REVIEWER").strip()
    return {"review_feedback": review}

def summarizer_node(state: AgentState):
    """汇总"""
    all_res = "\n".join([f"- {t['result']}" for t in state["task_list"]])
    final_ans = process_llm_call(call_llm(f"请汇总以下执行结果并友好回复用户：\n{all_res}"), "SUMMARIZER")
    return {"response": final_ans}



def assistant_node(state: AgentState):
    question = state.get("question")
    session_id = state.get("session_id", "default_user")
    
    # 1. 初始化或获取该 Session 的记忆
    history = sessions_history.get(session_id, [])
    facts = long_term_facts.get(session_id, "目前无特定背景信息。")

    # 2. 检查是否是“指令型”输入：要求记住某事
    if any(keyword in question for keyword in ["记住", "Remember", "remember"]):
        # 提取事实并存入长期库
        extract_prompt = f"请从以下话语中提取需要永久记住的事实，直接返回事实陈述，不要废话：{question}"
        new_fact = call_llm(extract_prompt)
        
        # 更新长期事实（跨对话存在）
        old_facts = long_term_facts.get(session_id, "")
        long_term_facts[session_id] = f"{old_facts} | {new_fact}".strip(" | ")
        
        response = f"✅ 没问题，我已经记住了：{new_fact}。在之后的对话中我会参考这条信息。"
        # 注意：存入指令本身不计入对话历史，避免干扰
        return {"response": response, "messages": history}

    # 3. 正常对话逻辑：注入长期事实作为背景
    system_prompt = {
        "role": "system", 
        "content": f"你是一个专业的 AI 助手。关于用户的已知长期事实：{long_term_facts.get(session_id, '无')}"
    }

    # 4. 修剪短期记忆
    if len(history) > MAX_MEMORY_NOTES:
        history = history[-MAX_MEMORY_NOTES:]

    # 5. 构造完整消息流并调用 LLM
    current_messages = [system_prompt] + history + [{"role": "user", "content": question}]
    response = call_llm(current_messages)

    # 6. 更新并保存短期记忆
    new_history = history + [{"role": "user", "content": question}, {"role": "assistant", "content": response}]
    sessions_history[session_id] = new_history

    return {
        "response": response,
        "messages": new_history
    }



def memory_manager_node(state: AgentState):
    user_input = state["question"]
    session_id = state.get("session_id", "default")
    
    # 关键词触发逻辑
    if "记住" in user_input or "remember" in user_input.lower():
        # 1. 调用 LLM 提取核心事实（去除语气词，只留干货）
        prompt = f"从以下话语中提取需要永久记忆的事实，直接返回事实陈述，不要废话: {user_input}"
        fact = call_llm(prompt).strip()
        
        # 2. 更新内存中的长期记忆
        # 获取旧记忆并合并
        old_memory = long_term_facts.get(session_id, "")
        updated_memory = f"{old_memory} | {fact}".strip(" | ")
        long_term_facts[session_id] = updated_memory
        
        # 3. Server 端控制台打印 (你要求的功能)
        print("\n" + "="*30)
        print(f"🚩 [SERVER LOG] 长期记忆已更新")
        print(f"📂 会话 ID: {session_id}")
        print(f"📝 存入事实: {fact}")
        print(f"📊 当前完整事实库: {updated_memory}")
        print("="*30 + "\n")
        
        return {"response": f"✅ 我已经把这个信息存入我的长期记忆库了：{fact}"}
    
    return {}


import json
from agent.state import AgentState

# def planner_node(state: AgentState):
#     """任务规划与局部修正节点"""
#     user_question = state.get("question", "")
#     task_list = state.get("task_list", [])
#     current_idx = state.get("current_step_index", 0)
#     feedback = state.get("review_feedback", "")

#     print(f"\n>>>> [SERVER PRINT] 进入 PLANNER 节点")

#     if not task_list:
#         # 首次进入：生成完整任务清单
#         print(f"正在为新需求生成初始规划: {user_question[:30]}...")
#         prompt = f"""你是一个任务规划专家。请将用户需求拆解为多个具体的、可执行的子步骤。
#         用户需求：{user_question}
#         请严格以 JSON 数组格式输出，每个对象包含 "task" 键。
#         示例：[{"{"}"task": "步骤1"{"}"}, {"{"}"task": "步骤2"{"}"}]"""
        
#         response = get_llm_answer(prompt)
#         try:
#             # 提取 JSON 部分
#             start = response.find("[")
#             end = response.rfind("]") + 1
#             tasks_raw = json.loads(response[start:end])
#             task_list = [{"task": t["task"], "status": "pending", "result": ""} for t in tasks_raw]
#             print(f"规划完成，共拆解为 {len(task_list)} 个步骤。")
#         except Exception as e:
#             print(f"JSON 解析失败，降级为单步处理。错误: {e}")
#             task_list = [{"task": user_question, "status": "pending", "result": ""}]
#     else:
#         # 递归修正：仅修改当前这一步
#         print(f"检测到评审反馈，正在修正第 {current_idx + 1} 步...")
#         print(f"反馈意见: {feedback}")
        
#         prompt = f"""你之前的任务描述是: {task_list[current_idx]['task']}
#         评审未通过，反馈意见是: {feedback}
#         请重新描述这一步，使其目标更明确。直接返回新的描述文字，不要带任何前缀。"""
        
#         new_desc = get_llm_answer(prompt)
#         task_list[current_idx]["task"] = new_desc
#         print(f"第 {current_idx + 1} 步已修正为: {new_desc}")

#     return {"task_list": task_list, "review_feedback": ""}

# def executor_node(state: AgentState):
#     """任务执行节点"""
#     idx = state["current_step_index"]
#     task_item = state["task_list"][idx]
    
#     print(f"\n>>>> [SERVER PRINT] 进入 EXECUTOR 节点")
#     print(f"正在执行第 {idx + 1} 步: {task_item['task']}")

#     # General Mode 下，Executor 主要根据任务描述生成内容
#     prompt = f"当前子任务: {task_item['task']}\n请给出详细的执行结果。"
#     result = get_llm_answer(prompt)
    
#     # 更新 state 中的任务结果
#     updated_list = list(state["task_list"])
#     updated_list[idx]["result"] = result
#     updated_list[idx]["status"] = "done"
    
#     print(f"第 {idx + 1} 步执行成功。")
#     return {"task_list": updated_list}

# def reviewer_node(state: AgentState):
#     """逻辑评审节点"""
#     idx = state["current_step_index"]
#     task_desc = state["task_list"][idx]["task"]
#     result = state["task_list"][idx]["result"]
    
#     print(f"\n>>>> [SERVER PRINT] 进入 REVIEWER 节点")
#     print(f"正在评审第 {idx + 1} 步的结果...")

#     prompt = f"""任务目标: {task_desc}
#     执行结果: {result}
#     请评审该结果是否逻辑合理。如果通过，请仅回复 'PASS'；
#     如果不通过，请回复 'FAIL: [具体原因]'。"""
    
#     review_res = get_llm_answer(prompt)
    
#     if "PASS" in review_res.upper():
#         print("评审通过 ✅")
#         return {"review_feedback": "PASS"}
#     else:
#         print(f"评审未通过 ❌ 原因: {review_res}")
#         return {"review_feedback": review_res}
    




# import json
# from agent.state import AgentState
# # 导入统一的 LLM 调用接口
# from utils.llm import call_llm
# from tools.schema_tool import get_schema
# from tools.sql_tool import run_sql
# from tools.analysis_tools import get_eda_statistics

# # --- 核心节点 ---

# def intent_node(state: AgentState):
#     """
#     意图识别节点：将用户请求分类为 data_analysis 或 general_question。
#     """
#     question = state["question"]
#     prompt = f"""
# Classify the user request.
# Categories:
# - data_analysis (if the user wants to query, analyze, or visualize data)
# - general_question (for general conversation or non-data tasks)

# Question: {question}

# Return only the category name.
# """
#     # 使用统一接口获取结果
#     result_text = call_llm(prompt).strip().lower()
    
#     # 清洗返回结果，确保只包含关键词
#     intent = "data_analysis" if "data_analysis" in result_text else "general_question"
    
#     # 初始化专家模式所需的计数器
#     return {
#         "intent": intent,
#         "retry_count": 0,
#         "error_msg": ""
#     }

# def schema_node(state: AgentState):
#     """
#     专家模式：提取当前数据库的 Schema。
#     """
#     schema = get_schema()
#     return {"schema": schema}

# def eda_node(state: AgentState):
#     """
#     专家模式：自动执行探索性数据分析 (EDA)。
#     """
#     stats = get_eda_statistics()
#     return {"eda_summary": stats}

# def planner_node(state: AgentState):
#     """
#     专家模式：基于 Schema 和 EDA 设计分析计划。
#     """
#     prompt = f"""
# Based on the Database Schema:
# {state['schema']} 

# And EDA Summary: 
# {state.get('eda_summary', 'No summary available')}

# Design a step-by-step logical plan to answer: {state['question']}
# """
#     plan = call_llm(prompt)
#     return {"plan": plan}

# def sql_node(state: AgentState):
#     """
#     执行节点：生成并运行 SQL 代码。包含错误反馈逻辑。
#     """
#     question = state["question"]
#     schema = state["schema"]
#     last_error = state.get("error_msg", "")
    
#     # 如果有上一次执行的错误信息，引导模型修复
#     error_feedback = f"\nPrevious SQL failed with error: {last_error}. Please fix the syntax or schema mismatch." if last_error else ""

#     prompt = f"""
# You are a SQL expert.
# Database schema:
# {schema}
# {error_feedback}

# Generate a SQL query to answer: {question}. 
# Return SQL ONLY. Do not include markdown tags like ```sql.
# """
#     query = call_llm(prompt).strip().replace("```sql", "").replace("```", "")
    
#     # 执行 SQL 工具
#     result = run_sql(query)
    
#     # 状态保存：判断执行结果是否包含错误标识
#     if isinstance(result, str) and "SQL Error" in result:
#         return {"sql_query": query, "error_msg": result, "query_result": None}
    
#     return {"sql_query": query, "error_msg": "", "query_result": result}

# def error_check_node(state: AgentState):
#     """
#     自愈检查节点：递增重试计数，状态供 graph.py 中的 error_router 使用。
#     """
#     current_retries = state.get("retry_count", 0)
    
#     if state.get("error_msg"):
#         # 记录日志，告知架构正在尝试自愈
#         print(f"--- Detected SQL Error. Incrementing retry count to {current_retries + 1} ---")
#         return {"retry_count": current_retries + 1}
    
#     return {"retry_count": current_retries}

# def visualization_node(state: AgentState):
#     """
#     可视化节点：生成 Plotly 代码块供前端渲染。
#     """
#     if not state.get("query_result"):
#         return {"figure_code": ""}

#     prompt = f"""
# Data: {state['query_result']}
# Question: {state['question']}

# Generate Python Plotly code to visualize this data. Return ONLY the code snippet.
# """
#     fig_code = call_llm(prompt)
#     return {"figure_code": fig_code}

# def insight_node(state: AgentState):
#     """
#     总结节点：针对通用回复或数据分析结果生成自然语言解释。
#     """
#     question = state["question"]
#     query_result = state.get("query_result")
    
#     if state["intent"] == "data_analysis" and query_result:
#         prompt = f"""
# User question: {question}
# Query result: {query_result}

# Summarize the key insights from this data in a clear, conversational way.
# """
#     else:
#         # 通用对话模式
#         prompt = f"Answer this question directly: {question}"

#     response = call_llm(prompt)
#     return {"response": response}