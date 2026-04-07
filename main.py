import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr


load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.4",   # 或者改成你的网关实际支持的模型名
    api_key=SecretStr("sk-846f1b178fbb2f6810f0cda48c69c9a7c2ffd29c8847887820bf7ee0a17a8945"),
    base_url="https://gmncode.cn",
    default_headers={
        "User-Agent": "codex_vscode/0.118.0-alpha.2 (Mac OS 26.2.0; arm64) unknown (VS Code; 26.325.31654)",
        # 如果中转服务对 stainless 头敏感，可以尝试置空（部分版本支持）
       "x-stainless-os": "Unknown",
        "x-stainless-lang": "python"
    },
    use_responses_api=True,
    reasoning_effort="high"
)

resp = llm.invoke("你好？")

print(resp)
