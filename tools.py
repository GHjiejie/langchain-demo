from model import chat_model_response

from langchain.agents import create_agent 

from langchain.messages import HumanMessage ,AIMessage

from langchain.tools import tool



async def exec_amount_transactions():
  """
  
  """


def get_weather(city:str) -> str:
  """Get the weather for a given city."""
  # Placeholder implementation - replace with actual weather API call
  return f"The weather in {city} is sunny."



agent = create_agent(
  model=chat_model_response,
  )

def extract_text_from_msg(msg) -> str:
    blocks = getattr(msg, "content_blocks", None) or getattr(msg, "content", [])
    parts = []

    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))

    return "".join(parts)

for chunk in agent.stream(
  {"messages": [{"role": "user", "content": "上海的天气怎么样？"}]},
  stream_mode=["messages","updates"],
  version="v2",
):
  print(f"Event-Type: {chunk}")
  print("\n")






