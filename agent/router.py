# def route(state):
#     # 1. 如果意图不是数据分析，直接去 insight 节点回复
#     if state["intent"] != "data_analysis":
#         return "insight"
    
#     # 2. 如果 SQL 报错且重试次数少于 3 次，路由回 'sql' 节点进行修复
#     if state.get("error_msg") and state.get("retry_count", 0) < 3:
#         # 手动增加计数（架构师可以在此处打印日志模拟 Manus 的思考过程）
#         state["retry_count"] = state.get("retry_count", 0) + 1
#         print(f"--- 触发反思机制：正在进行第 {state['retry_count']} 次 SQL 纠错 ---")
#         return "sql"
        
#     return "insight"

# def route(state):
#     # 如果意图是数据分析且你在代码中检测到了数据库环境，走 Expert 路径
#     if state["intent"] == "data_analysis":
#         return "schema"
#     # 否则一律走 General 路径 (你的 insight 节点或新增一个 general 节点)
#     return "insight"
# 修改 CS5260-project/DAS-Agent/agent/router.py
from agent.state import AgentState

def pre_processor_router(state: AgentState):
    """判断是直接结束还是进入规划"""
    if state.get("intent") == "memory_done":
        return "end"
    return "plan"

def review_router(state: AgentState):
    """评审后的流转逻辑"""
    feedback = state.get("review_feedback", "")
    current_idx = state.get("current_step_index", 0)
    total_steps = len(state.get("task_list", []))

    if "PASS" in feedback.upper():
        if current_idx + 1 < total_steps:
            # 更新索引并进入下一步执行
            state["current_step_index"] += 1
            return "next_step"
        return "finish"
    else:
        # 评审不通过，回流到 Planner 修正描述
        return "replan"