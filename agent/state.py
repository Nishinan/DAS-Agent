from typing import Dict, TypedDict, List, Any, Annotated
from langgraph.graph.message import add_messages


from typing import TypedDict

from typing import TypedDict, List, Dict, Any
from typing import TypedDict, List, Dict, Any
# 修改 CS5260-project/DAS-Agent/agent/state.py
from typing import Dict, TypedDict, List, Any, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    question: str
    response: str
    intent: str
    retry_count: int
    messages: List[Dict]
    session_id: str
    
    # --- 为类 Manus 功能新增的最小化字段 ---
    task_list: List[Dict[str, Any]]  # 格式: [{"task": "描述", "status": "pending", "result": ""}]
    current_step_index: int         # 当前执行到的步骤索引
    review_feedback: str            # Reviewer 的反馈意见

# class AgentState(TypedDict):
#     question: str
#     intent: str
#     schema: str
#     # --- 新增字段 ---
#     eda_summary: str      # 存储数据的统计摘要
#     plan: str             # 存储生成的分析计划
#     sql_query: str
#     query_result: Any
#     error_msg: str        # 存储 SQL 错误信息
#     figure_code: str      # 存储生成的绘图代码
#     response: str
#     retry_count: int      # 故障自愈计数
#     selected_model: str   # 预留：给未来前端传参用