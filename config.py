import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACTIVE_MODEL_PROVIDER = os.getenv("ACTIVE_MODEL_PROVIDER", "huggingface")

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = "gpt-4o"

# Hugging Face 配置
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_API_URL = os.getenv("HF_API_URL") # 对应环境变量中的 https://router.huggingface.co/v1/chat/completions

# 明确指定你要求的模型 ID
HF_MODEL_ID = "Qwen/Qwen3.5-9B:together" 

def query_model(prompt):
    """
    适配 v1/chat/completions 的底层调用函数
    """
    headers = {"Content-Type": "application/json"}
    if HF_API_TOKEN:
        headers["Authorization"] = f"Bearer {HF_API_TOKEN}"

    # 构造兼容 OpenAI 的 Payload
    payload = {
        "model": HF_MODEL_ID,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500,
        "temperature": 0.2
    }

    response = requests.post(HF_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise Exception(f"HF API error {response.status_code}: {response.text}")

    result = response.json()
    # 按照 OpenAI 格式解析返回内容
    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"]
    return str(result)

DATABASE_URI = "sqlite:///data.db"