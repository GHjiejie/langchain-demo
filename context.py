from model import chat_model_response
from typing import Any, NotRequired
from langchain.agents import create_agent ,AgentState

from langchain.messages import HumanMessage ,AIMessage
from langgraph.runtime import Runtime
from langchain.agents.middleware import before_agent,before_model,after_agent,after_model

from langchain.tools import tool
from pydantic import BaseModel


# 第一件事是 会话内短期记忆。默认 agent 用 AgentState 管理短期记忆，核心就是 messages 这个字段，也就是当前线程里的消息历史。只要这些消息还在 state 里，模型下一次调用时就能继续看到它们。要让这种记忆跨多轮 invoke/stream 保留下来，需要给 agent 配 checkpointer，并在调用时传 thread_id；否则每次调用都会从一个新会话开始。

# 第二件事是 运行时上下文 context。这不是聊天历史，而是“本次运行的静态配置”，比如用户 ID、角色、数据库连接、特征开关之类。官方文档明确说了：runtime context 是依赖注入；它不会自动进入模型提示词，只有当工具、中间件或其他逻辑主动去读它，并把它加进消息或系统提示里时，模型才“看得见”。context_schema 用来声明这个上下文的数据结构，文档推荐使用 dataclass 或 TypedDict。


class CustomContext(BaseModel):
    name:str
    age:int
    sex:str
    tel:str


class NormalConText(BaseModel):
    user_id: str
    role: str


class CustomState(AgentState):
    user_name: NotRequired[str]
    phone: str



def get_weather(city:str) -> str:
  """Get the weather for a given city."""
  # Placeholder implementation - replace with actual weather API call
  return f"The weather in {city} is sunny."


@before_agent
def before_agent_middleware(state:CustomState, runtime: Runtime[CustomContext]) -> dict[str, Any] | None:
   print(f"Before agent: {runtime.context}")
   # 在 before_agent 中把 runtime.context 同步到 state
   return {"user_name": runtime.context.name, "phone": runtime.context.tel}

@before_model
def before_model_middleware(state: CustomState, runtime: Runtime[CustomContext]) -> dict[str, Any] | None:
   print(f"Before model: {runtime.context}")
  
   return None

@after_agent
def after_agent_middleware(state: CustomState, runtime: Runtime[CustomContext]) -> dict[str, Any] | None:
   print(f"After agent: {runtime.context}")
   print(f"State:{state}")
   return None

@after_model
def after_model_middleware(state: CustomState, runtime: Runtime[CustomContext]) -> dict[str, Any] | None:
   print(f"After model: {runtime.context}")
   print(f"State:{state}")
   return None

agent = create_agent(
  model=chat_model_response,
  middleware=[before_agent_middleware, before_model_middleware, after_agent_middleware, after_model_middleware],
  state_schema=CustomState,
  context_schema=CustomContext,
  )



def extract_text_from_msg(msg) -> str:
    blocks = getattr(msg, "content_blocks", None) or getattr(msg, "content", [])
    parts = []

    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "text":
            parts.append(block.get("text", ""))

    return "".join(parts)

for chunk in agent.stream(
  {"messages": [{"role": "user", "content": "你是谁？"}] },
    stream_mode=["messages", "updates"],
    version="v2",
    context=CustomContext(name="zhengjie", age=24, sex="male", tel="19168972650"),
):
   
  if chunk["type"] == "messages":
     message_chunk, metadata = chunk["data"]
     print(f"content: {message_chunk.content_blocks}")
     print("\n")

  
  
