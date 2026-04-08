from model import chat_model_response

from langchain.agents import create_agent 

from langchain.messages import HumanMessage ,AIMessage

from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents.middleware import HumanInTheLoopMiddleware

from langchain_core.runnables import RunnableConfig

from langgraph.types import Command






def del_user(user_id:str) -> str:
  """Delete a user by ID."""
  # Placeholder implementation - replace with actual user deletion logic
  return f"User with ID {user_id} has been deleted."

agent = create_agent(
  model=chat_model_response,
  tools=[del_user],
  middleware=[
     HumanInTheLoopMiddleware(
        interrupt_on={
           "del_user":{
              "allowed_decisions": ["approve", "reject"]
           }
        }
     )
  ],
  checkpointer=InMemorySaver(),
  )

custom_config: RunnableConfig = {
    "configurable": {"thread_id": "123"}
}

def extract_text_from_msg(msg) -> str:
    blocks = getattr(msg, "content_blocks", None) or getattr(msg, "content", [])
    parts = []

    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))

    return "".join(parts)

# 第一次调用，会被中断
for chunk in agent.stream(
  {"messages": [{"role": "user", "content": "请你删除id为123的用户"}]},
  stream_mode=["messages","updates"],
  version="v2",
  config=custom_config,
):
  print(f"Event-Type: {chunk}")
  print("\n")


print("-----------允许执行-----------")

# 下面的这个操作实际上是用户在页面上输入反馈的结果

for chunk in agent.stream(
   Command(
      resume={
         "decisions":[
            {"type":"approve"}
         ]
      }
   ),
   stream_mode=["messages", "updates"],
    version="v2",
    config=custom_config,
):
   print(f"Event-Type: {chunk}")
   print("\n")



