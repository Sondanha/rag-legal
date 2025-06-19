from langgraph.graph import StateGraph
from graph.nodes.embed_node import embed_query_runnable
from graph.nodes.retrieve_ordin_node import retrieve_ordin_runnable
from graph.nodes.retrieve_law_node import retrieve_law_runnable
from graph.nodes.retrieve_number_node import retrieve_number_runnable
from graph.nodes.final_prompt_node import final_prompt_runnable
from graph.nodes.llm_node import call_llm_node_runnable

from typing import TypedDict, List

class RAGState(TypedDict):
    query: str
    embedding: List[float]
    messages: List[dict]
    past_dialogue: str
    ordin_docs: List[dict]
    law_docs: List[dict]
    number_docs: List[dict]
    prompt: str
    response: str

def build_rag_graph():
    builder = StateGraph(state_schema=RAGState)

    builder.add_node("embed", embed_query_runnable)
    builder.add_node("retrieve_ordin", retrieve_ordin_runnable)
    builder.add_node("retrieve_law", retrieve_law_runnable)
    builder.add_node("retrieve_number", retrieve_number_runnable)
    builder.add_node("final_prompt", final_prompt_runnable)
    builder.add_node("call_llm", call_llm_node_runnable)

    builder.set_entry_point("embed")
    builder.add_edge("embed", "retrieve_ordin")
    builder.add_edge("retrieve_ordin", "retrieve_law")
    builder.add_edge("retrieve_law", "retrieve_number")  
    builder.add_edge("retrieve_number", "final_prompt") 
    builder.add_edge("final_prompt", "call_llm")
    builder.set_finish_point("call_llm")

    return builder.compile()