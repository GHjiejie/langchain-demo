from model import chat_model_response

from langchain.agents import create_agent 

from langchain.messages import HumanMessage ,AIMessage

from langchain.tools import tool
from langgraph.checkpoint.memory import InMemorySaver

from langchain.agents.middleware import HumanInTheLoopMiddleware

from langchain_core.runnables import RunnableConfig

from langgraph.types import Command
from typing import TypedDict,Annotated
import operator

from langgraph.graph import StateGraph,START,END

# 2) 图状态
# 这里我故意用“不同 key”而不是 list + reducer，
# 这样更容易看懂并行后的结果分别落在哪里。
class State(TypedDict):
    user_request: str
    code_prompt: str
    doc_prompt: str
    code_report: str
    doc_report: str
    final_answer: str




# 3) 规划节点：把一个请求拆成两个并行子任务
def plan(state: State):
    req = state["user_request"]
    return {
        "code_prompt": (
            "你是代码审查专家。\n"
            "请只从代码实现角度分析下面这个需求可能出现的问题，"
            "重点看空指针、边界条件、异常处理、健壮性。\n\n"
            f"用户请求：{req}"
        ),
        "doc_prompt": (
            "你是需求文档审查专家。\n"
            "请只从需求文档/规格说明角度分析下面这个需求可能缺失的约束，"
            "重点看异常处理、输入输出定义、边界场景、歧义点。\n\n"
            f"用户请求：{req}"
        ),
    }


# 4) 并行分支 A：代码专家
def code_agent(state: State):
    resp = chat_model_response.invoke([
        {"role": "system", "content": "你是一个非常严谨的代码实现审查助手。"},
        {"role": "user", "content": state["code_prompt"]},
    ])
    return {"code_report": resp.content}

# 5) 并行分支 B：文档专家
def doc_agent(state: State):
    resp = chat_model_response.invoke([
        {"role": "system", "content": "你是一个非常严谨的需求/规格审查助手。"},
        {"role": "user", "content": state["doc_prompt"]},
    ])
    return {"doc_report": resp.content}

# 6) 汇总节点：把两个专家的结果合并
def merge(state: State):
    resp = chat_model_response.invoke([
        {
            "role": "system",
            "content": (
                "你是总控 supervisor。\n"
                "请把两个专家的分析合并成一份简洁的最终结论：\n"
                "1. 先列共同问题\n"
                "2. 再列代码实现问题\n"
                "3. 再列需求文档问题\n"
                "4. 最后给一个改进建议\n"
            ),
        },
        {
            "role": "user",
            "content": (
                f"用户原始请求：{state['user_request']}\n\n"
                f"【代码专家输出】\n{state['code_report']}\n\n"
                f"【文档专家输出】\n{state['doc_report']}"
            ),
        },
    ])
    return {"final_answer": resp.content}


builder=StateGraph(State)

builder.add_node("plan", plan)
builder.add_node("code", code_agent)
builder.add_node("doc", doc_agent)
builder.add_node("merge", merge)

builder.add_edge(START, "plan")
builder.add_edge("plan", "code")
builder.add_edge("plan", "doc")
builder.add_edge("code", "merge")
builder.add_edge("doc", "merge")
builder.add_edge("merge", END)

graph = builder.compile()

# 8) 流式执行
final_answer = ""
last_node = None

for chunk in graph.stream(
    {
        "user_request": "请同时检查代码实现和需求文档是否一致",
        "code_prompt": "",
        "doc_prompt": "",
        "code_report": "",
        "doc_report": "",
        "final_answer": "",
    },
    # 同时拿 token 流 + 节点更新
    stream_mode=["messages", "updates"],
    version="v2",
):
    if chunk["type"] == "messages":
        msg, metadata = chunk["data"]
        node_name = metadata["langgraph_node"]

        if msg.content:
            # 为了防止并行节点的 token 混在一起看不懂，
            # 这里按节点名打印前缀
            if node_name != last_node:
                print(f"\n\n[{node_name}]")
                last_node = node_name
            print(msg.content, end="", flush=True)

    elif chunk["type"] == "updates":
        for node_name, update in chunk["data"].items():
            print(f"\n\n✅ {node_name} 完成，更新字段: {list(update.keys())}")
            if node_name == "merge" and "final_answer" in update:
                final_answer = update["final_answer"]

print("\n\n================ 最终结果 ================\n")
print(final_answer)












