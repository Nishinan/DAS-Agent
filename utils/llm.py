import requests
import openai
from config import (
    ACTIVE_MODEL_PROVIDER, 
    OPENAI_API_KEY, OPENAI_MODEL_NAME,
    HF_API_TOKEN, HF_API_URL, HF_MODEL_ID
)

def call_llm(input_data):
    """
    input_data 可以是字符串 (旧版兼容)，也可以是 
    list (记忆模式: [{"role": "user", "content": "..."}, ...])
    """
    # 统一格式化为 messages 列表
    if isinstance(input_data, str):
        messages = [{"role": "user", "content": input_data}]
    else:
        messages = input_data

    if ACTIVE_MODEL_PROVIDER == "openai":
        return _call_openai(messages)
    elif ACTIVE_MODEL_PROVIDER == "huggingface":
        return _call_huggingface_stream(messages)
    else:
        raise ValueError(f"Unsupported provider: {ACTIVE_MODEL_PROVIDER}")

def _call_openai(messages: list):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=messages # 直接传入列表
    )
    return response.choices[0].message.content
import requests
import json

def _call_huggingface_stream(messages: list):
    # ... headers 和 payload 保持不变 (包含 stream: True) ...
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "Qwen/Qwen3.5-9B:together",
        "messages": messages,
        "max_tokens": 1024,
        "temperature": 0.7,
        "stream": True  # 👈 核心：开启流式开关
    }
    
    response = requests.post(HF_API_URL, headers=headers, json=payload, stream=True, timeout=60)
    
    for line in response.iter_lines():
        if not line:
            continue
            
        line_str = line.decode('utf-8').strip()
        
        # 1. 过滤掉不以 data: 开头的行
        if not line_str.startswith("data: "):
            continue
            
        data_str = line_str[6:].strip()
        
        # 2. 检查结束信号
        if data_str == "[DONE]":
            break
            
        try:
            data_json = json.loads(data_str)
            
            # 3. 核心修复：增加对 choices 的安全性检查
            if "choices" in data_json and len(data_json["choices"]) > 0:
                delta = data_json["choices"][0].get("delta", {})
                content = delta.get("content", "")
                
                if content:
                    yield content
            else:
                # 打印一下跳过了哪些空行，方便调试
                # print(f"DEBUG: 跳过无内容行: {data_str}")
                pass
                
        except json.JSONDecodeError:
            print(f"DEBUG: 忽略非 JSON 行: {line_str}")
            continue