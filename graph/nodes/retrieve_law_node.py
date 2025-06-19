from langchain_core.runnables import RunnableLambda
from retriever.qdrant_retriever import search_law_collection

def retrieve_law_docs(state: dict) -> dict:
    embedding = state["embedding"]
    law_docs = search_law_collection(embedding)

    return {
        **state,
        "law_docs": law_docs
    }

retrieve_law_runnable = RunnableLambda(retrieve_law_docs)
