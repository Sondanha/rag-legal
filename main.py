from fastapi import FastAPI
from pydantic import BaseModel
from graph.rag_graph import build_rag_graph

app = FastAPI()
graph = build_rag_graph()

class QueryRequest(BaseModel):
    query: str

@app.post("/rag")
async def rag_query(request: QueryRequest):
    result = graph.invoke({"query": request.query})
    return {"response": result["response"]}