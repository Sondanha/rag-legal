from langchain_core.runnables import RunnableLambda
from retriever.qdrant_retriever import search_number_collection
from typing import Dict, Any

# 🔹 강남구 동 리스트
GANGNAM_DONGS = [
    "신사동", "논현동", "압구정동", "청담동", "삼성동", "대치동", "역삼동",
    "도곡동", "개포동", "세곡동", "일원동", "수서동"
]

# 🔹 사용자 쿼리에서 포함된 지역명 추출
def extract_region_from_query(query: str, region_list: list[str]) -> list[str]:
    return [dong for dong in region_list if dong in query]

# 🔹 LangGraph용 노드 함수
def retrieve_number(state: Dict[str, Any]) -> Dict[str, Any]:
    embedding = state["embedding"]
    query = state.get("query", "")
    
    # Qdrant 검색
    number_docs = search_number_collection(embedding)

    # 🔍 지역 필터링
    region_names = extract_region_from_query(query, GANGNAM_DONGS)
    if region_names:
        number_docs = [
            doc for doc in number_docs
            if any(region in doc.get("부서명", "") for region in region_names)
        ]

    return {
        **state,
        "number_docs": number_docs
    }

retrieve_number_runnable = RunnableLambda(retrieve_number)