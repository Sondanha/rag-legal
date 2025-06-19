from retriever.qdrant_retriever import search_ordin_collection
from langchain_core.runnables import RunnableLambda

def retrieve_ordin_docs(state: dict) -> dict:
    """
    Qdrant 조례 컬렉션에서 유사 문서 검색
    입력: { "embedding": list[float] }
    출력: { ..., "ordin_docs": list[dict] }
    """
    embedding = state["embedding"]
    hits = search_ordin_collection(embedding, top_k=10)
    state["ordin_docs"] = hits  
    return state


retrieve_ordin_runnable = RunnableLambda(retrieve_ordin_docs)
