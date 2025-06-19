from langchain_core.runnables import RunnableLambda
import requests, os
from dotenv import load_dotenv

load_dotenv()
EMBEDDING_SERVER_URL = os.getenv("EMBEDDING_SERVER_URL")

def embed_query(state: dict) -> dict:
    query = state["query"]
    res = requests.post(f"{EMBEDDING_SERVER_URL}/embed", json={"texts": [query]}, timeout=10)
    embedding = res.json()["embeddings"][0]
    return {**state, "embedding": embedding}

embed_query_runnable = RunnableLambda(embed_query)