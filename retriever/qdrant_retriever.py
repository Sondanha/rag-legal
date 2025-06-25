import os
from typing import List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
from dotenv import load_dotenv

load_dotenv()

ORDIN_COLLECTION = os.getenv("COLLECTION_NAME_ORDIN")
LAW_COLLECTION = os.getenv("COLLECTION_NAME_LAW")
NUMBER_COLLECTION = os.getenv("COLLECTION_NAME_NUMBER")

qdrant = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)

# 공통 검색
def search_qdrant(collection_name: str, query_vector: List[float], top_k: int = 10) -> List[dict]:
    """
    지정된 Qdrant 컬렉션에서 query_vector에 가장 유사한 top_k 문서를 반환
    """
    results = qdrant.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True
    )
        
    return [hit.payload for hit in results]

# 조례 검색
def search_ordin_collection(query_vector: List[float], top_k: int = 7) -> List[dict]:
    return search_qdrant(ORDIN_COLLECTION, query_vector, top_k)

# 법률 검색
def search_law_collection(query_vector: List[float], top_k: int = 7) -> List[dict]:
    return search_qdrant(LAW_COLLECTION, query_vector, top_k)

# 전화번호 검색 
def search_number_collection(query_vector: List[float], top_k: int = 3) -> List[dict]:
    return search_qdrant(NUMBER_COLLECTION, query_vector, top_k)
