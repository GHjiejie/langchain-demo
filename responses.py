import os

import dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model


dotenv.load_dotenv()

chat_model = init_chat_model(
    model="gpt-5.4",
    api_key=os.getenv("API_KEY"),
    base_url=os.getenv("BASE_URL"),
    default_headers={
        "User-Agent": "codex_vscode/0.118.0-alpha.2 (Mac OS 26.2.0; arm64) unknown (VS Code; 26.325.31654)",
        "x-stainless-os": "Unknown",
        "x-stainless-lang": "python",
    },
    use_responses_api=True,
)

agent = create_agent(model=chat_model)


def extract_text(message_chunk) -> str:
    text = getattr(message_chunk, "text", "") or ""
    if text:
        return text

    parts = []
    for block in getattr(message_chunk, "content", []) or []:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))
    return "".join(parts)


full_text = []
for event in agent.stream(
    {"messages": [{"role": "user", "content": "你是谁？"}]},
    stream_mode="messages",
    version="v2",
):
    
    if event["type"] != "messages":
        continue

    message_chunk, metadata = event["data"]

    print(f"message_chunk: {message_chunk}")
    print("\n")
    
    if metadata.get("langgraph_node") != "model":
        continue

    text = extract_text(message_chunk)
    if not text:
        continue

    print(text, end="", flush=True)
    full_text.append(text)

print("\n")
print("Final text:", "".join(full_text))
