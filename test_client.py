import requests
import json

def test_stream():
    url = "http://localhost:8000/api/chat/stream"
    payload = {"message": "hi"}
    
    # 模拟前端的 POST 请求
    response = requests.post(url, json=payload, stream=True)
    
    print(f"状态码: {response.status_code}")
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            print(f"收到帧: {decoded_line}")
            if decoded_line.startswith("data: "):
                try:
                    content = json.loads(decoded_line[6:])
                    # 模拟前端解析 payload.delta
                    delta = content.get("payload", {}).get("delta")
                    print(f"解析到的文本: {delta}")
                except Exception as e:
                    print(f"❌ 解析失败: {e}")

if __name__ == "__main__":
    test_stream()