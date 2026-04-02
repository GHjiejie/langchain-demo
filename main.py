import os

from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage, AIMessage
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langchain.agents import create_agent
from typing import TypedDict
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.config import get_stream_writer
import dotenv

dotenv.load_dotenv()


chat_model = init_chat_model(
    model="claude-opus-4-6",
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY"),
)
print(chat_model)


system_msg = SystemMessage("You are a helpful assistant.")
human_msg = HumanMessage("Hello, how are you?")

# Use with chat models
messages = [system_msg, human_msg]
response = chat_model.invoke(messages)
print(response)
