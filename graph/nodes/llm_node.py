from langchain_core.runnables import RunnableLambda
from llm.call_llm import call_llm  # Gemini 호출 함수

def call_llm_node(state: dict) -> dict:
    """
    LangGraph Node: 최종 프롬프트를 LLM에 전달하고 응답을 받아오는 노드
    입력: { "prompt": str }
    출력: { ..., "response": str }
    """
    prompt = state["prompt"]
    response = call_llm(prompt)

    return {**state, "response": response}

call_llm_node_runnable = RunnableLambda(call_llm_node)
