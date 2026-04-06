# DAS-Agent: 智能数据分析与通用对话平台

本项目是为 CS5260 课程开发的 AI Agent，旨在通过自然语言实现复杂的任务处理。系统集成了类似 Manus 的任务编排能力，支持通用对话与深度数据分析（Expert Mode）。

## 核心功能
- **通用模式 (General Mode)**: 基于大模型的自然语言对话。
- **专家模式 (Expert Mode)**: 
  - 支持 CSV 文件上传与自动 SQL 数据库建表。
  - 自然语言转 SQL 自动化查询。
  - 自动错误检测与查询修复。
- **实时交互**: 支持流式 (SSE) 文本输出与数据可视化预览。

## 技术栈
- **后端**: FastAPI, LangGraph, LangChain, SQLite
- **前端**: Vanilla JS, SSE 流式渲染, CSS Grid 布局

## 启动手册

### 1. 环境准备
确保你的环境中已安装 Python 3.10+。
安装依赖：
```bash
pip install fastapi uvicorn langgraph langchain_openai pandas sqlalchemy


# DAS-Agent (CS5260 Project)

这是一个模仿 Manus 的数据分析 AI Agent。它能识别用户意图，自动将 CSV 转换为 SQL 数据库并生成洞察。

## 快速启动手册

1. **配置环境**:
   在根目录下创建 `.env` 文件，填入：
   ```env
   HF_API_TOKEN=你的HuggingFace令牌

```

2. **放置前端**:
确保你的目录结构如下：
* `/DAS-Agent` (本仓库)
* `/CS5260-main/frontend` (前端文件夹)


3. **启动后端**:
```bash
python main.py

```


既然你将模型后端从 OpenAI 切换到了 **Hugging Face Inference API**，并且指定了 `mistral-small` 模型，你确实需要修改 **`utils/llm.py`** 中的调用逻辑。

OpenAI 的 SDK 格式与 Hugging Face 的请求格式不同，你需要从原先的 `openai` 库切换为 `requests` 或者使用 Hugging Face 的官方 Python 库。

以下是针对你的修改建议：

### 1. 修改 `utils/llm.py`

你需要重写 `call_llm`（或类似命名的函数），使其能够向 Hugging Face API 发送请求。

```python
import requests
from config import HF_API_TOKEN, HF_API_URL

def call_llm(prompt: str):
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "return_full_text": False
        }
    }
    
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        # Hugging Face 返回的是一个列表 [ {"generated_text": "..."} ]
        result = response.json()
        return result[0]['generated_text']
    else:
        raise Exception(f"HF API Error: {response.status_code} - {response.text}")

```

### 2. 检查 `agent/nodes.py` (重要)

Mistral 模型的 Prompt 格式与 GPT-4 不同。

* **Prompt 格式**：Mistral 通常使用 `[INST] ... [/INST]` 标签。你需要确保你的 `intent_node` 和 `insight_node` 里的提示词适配 Mistral。
* **输出解析**：Mistral-small 的逻辑推理能力与 GPT-4 有差异，你需要检查 `intent_node` 返回的是否仍然是纯净的 `data_analysis` 或 `general_question` 字符串。如果它带了多余的解释，`router.py` 的判断会失效。

### 3. 修改 `requirements.txt`

如果之前只安装了 OpenAI，现在需要添加 `requests`：

```text
requests
python-dotenv
# ... 其他依赖

```

### 4. 架构更新：项目结构与启动手册

目前你的 Agent 结构如下：

#### 核心结构图

* **中枢 (main.py)**: 负责 FastAPI 路由、文件上传和 SSE 流式推送。
* **图逻辑 (agent/graph.py)**: 定义了从 `intent` 到 `insight` 的拓扑路径。
* **工具层 (tools/)**: 包含 SQL 生成 (`sql_tool.py`) 和表结构提取 (`schema_tool.py`)。
* **状态管理 (agent/state.py)**: 维护全剧会话状态 `AgentState`。

---

#### 简易 README.md

```markdown
# DAS-Agent (CS5260 Project)

这是一个模仿 Manus 的数据分析 AI Agent。它能识别用户意图，自动将 CSV 转换为 SQL 数据库并生成洞察。

## 快速启动手册

1. **配置环境**:
   在根目录下创建 `.env` 文件，填入：
   ```env
   HF_API_TOKEN=你的HuggingFace令牌

```

2. **放置前端**:
确保你的目录结构如下：
* `/DAS-Agent` (本仓库)
* `/CS5260-main/frontend` (前端文件夹)


3. **启动后端**:
```bash
python main.py

```


程序会自动挂载 `../CS5260-main/frontend` 并在 `http://localhost:8000` 运行。
4. **项目内容**:
* **自动建表**: 上传 CSV 后自动初始化 SQLite。
* **智能路由**: 自动区分“闲聊”与“数据任务”。
* **流式反馈**: 前端实时显示 AI 思考过程。



```

**下一步建议：**
由于你切换到了 Mistral，需要我帮你优化一下 `nodes.py` 里的提示词（Prompt），以防模型输出格式不符合 `router.py` 的要求吗？

```
4. **项目内容**:
* **自动建表**: 上传 CSV 后自动初始化 SQLite。
* **智能路由**: 自动区分“闲聊”与“数据任务”。
* **流式反馈**: 前端实时显示 AI 思考过程。



