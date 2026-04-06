from langgraph.graph import StateGraph, END
from agent.state import AgentState
# from agent.nodes import (
#     intent_node, 
#     schema_node, 
#     eda_node, 
#     planner_node, 
#     sql_node, 
#     error_check_node, 
#     visualization_node, 
#     insight_node
# )

from agent.nodes import assistant_node

def mode_router(state: AgentState):
    """
    根据意图识别结果分发模式：
    - 如果是数据分析意图，进入专家模式链路（从 schema 开始）
    - 否则进入通用回复模式（直接由 insight 总结）
    """
    if state.get("intent") == "data_analysis":
        return "schema"
    return "insight"

def error_router(state: AgentState):
    """
    故障自愈路由逻辑：
    - 如果存在错误信息 (error_msg) 且重试次数 (retry_count) 小于 3 次，回跳修复。
    - 否则（成功或超过重试次数）进入可视化阶段。
    """
    error = state.get("error_msg")
    retries = state.get("retry_count", 0)
    
    if error and retries < 3:
        return "repair"
    return "visualize"



from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes import assistant_node


from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes import (
    planner_node, 
    executor_node, 
    reviewer_node, 
    summarizer_node)

# 修改 CS5260-project/DAS-Agent/agent/graph.py
from langgraph.graph import StateGraph, START, END
from agent.state import AgentState
from agent.nodes import (
    pre_processor_node, planner_node, executor_node, 
    reviewer_node, summarizer_node
)
from agent.router import pre_processor_router, review_router

def build_graph():
    workflow = StateGraph(AgentState)

    # 1. 注册节点
    workflow.add_node("pre_processor", pre_processor_node)
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("summarizer", summarizer_node)

    # 2. 设置入口
    workflow.add_edge(START, "pre_processor")

    # 3. 记忆指令检查路由
    workflow.add_conditional_edges(
        "pre_processor",
        pre_processor_router,
        {
            "end": END,
            "plan": "planner"
        }
    )

    # 4. 任务循环链路
    workflow.add_edge("planner", "executor")
    workflow.add_edge("executor", "reviewer")

    # 5. 评审反馈路由 (Re-planning 核心)
    workflow.add_conditional_edges(
        "reviewer",
        review_router,
        {
            "replan": "planner",      # 局部修改当前步骤
            "next_step": "executor",   # 执行下一项
            "finish": "summarizer"     # 总结结果
        }
    )

    workflow.add_edge("summarizer", END)
    return workflow.compile()

# def build_graph():
#     # 1. 初始化图，使用你的 AgentState
#     workflow = StateGraph(AgentState)

#     # 2. 添加唯一的通用节点
#     workflow.add_node("assistant", assistant_node)

#     # 3. 设置起终点：直接进入 assistant 并结束
#     workflow.add_edge(START, "assistant")
#     workflow.add_edge("assistant", END)

#     return workflow.compile()

# def build_graph():
#     # 初始化状态图，使用定义的 AgentState
#     workflow = StateGraph(AgentState)

#     # 1. 添加所有功能节点
#     workflow.add_node("intent", intent_node)               # 意图识别（架构中枢）
#     workflow.add_node("schema", schema_node)               # 表结构提取（专家模式起点）
#     workflow.add_node("eda", eda_node)                     # 自动化探索性数据分析
#     workflow.add_node("planner", planner_node)             # 任务步骤规划
#     workflow.add_node("sql", sql_node)                     # SQL 代码生成/修复
#     workflow.add_node("error_check", error_check_node)     # 运行 SQL 并检查错误
#     workflow.add_node("visualization", visualization_node) # 数据可视化渲染
#     workflow.add_node("insight", insight_node)             # 最终洞察总结（General 模式也用此节点）

#     # 2. 设置入口
#     workflow.set_entry_point("intent")
    
#     # 3. 构建条件路由与连线
    
#     # A. 意图分发：决定进入 General 还是 Expert 模式
#     workflow.add_conditional_edges(
#         "intent", 
#         mode_router, 
#         {
#             "schema": "schema",
#             "insight": "insight"
#         }
#     )

#     # B. 专家模式主链路
#     workflow.add_edge("schema", "eda")
#     workflow.add_edge("eda", "planner")
#     workflow.add_edge("planner", "sql")
#     workflow.add_edge("sql", "error_check")

#     # C. 故障自愈循环：如果 SQL 报错，跳回 sql 节点修复，最多 3 次
#     workflow.add_conditional_edges(
#         "error_check", 
#         error_router, 
#         {
#             "repair": "sql",
#             "visualize": "visualization"
#         }
#     )

#     # D. 收尾链路
#     workflow.add_edge("visualization", "insight")
#     workflow.add_edge("insight", END)

#     # 4. 编译图
#     return workflow.compile()