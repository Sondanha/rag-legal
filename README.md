# 🧠 RAG Legal System

LLM + LangGraph 기반 법률 질의응답 시스템입니다.  
FastAPI로 API 서버를 구성하고, Cloudtype 및 Hugging Face Spaces를 통해 배포됩니다.

---

## 🚀 Features

- ✅ LangGraph 기반 RAG 파이프라인
- ✅ Qdrant 벡터 검색 연동
- ✅ Google Gemini API 호출
- ✅ Hugging Face Spaces 기반 임베딩 서버 연동
- ✅ FastAPI API 서버 (`/ping`, `/rag`)

---

## 🗂 프로젝트 구조

```
rag-api/
│
├── graph/
│ ├── rag_graph.py
│ └── nodes/
│ ├── embed_node.py
│ ├── final_prompt_node.py
│ ├── llm_node.py
│ ├── retrieve_ordin_node.py
│ ├── retrieve_law_node.py
│ └── retrieve_number_node.py
│
├── llm/
│ └── call_llm.py
│
├── retriever/
│ └── qdrant_retriever.py
│
├── main.py # FastAPI 앱 진입점
├── requirements.txt
├── Dockerfile
├── cloudtype.yaml # Cloudtype 배포 설정
└── .env # 환경 변수 (Git에 제외)
```

---

## 🔧 환경 변수 예시 (`.env`)

```env
QDRANT_URL=https://your-qdrant-url
QDRANT_API_KEY=your-qdrant-api-key

GOOGLE_API_KEY=your-google-genai-key

EMBEDDING_MODEL_NAME=intfloat/multilingual-e5-base
EMBEDDING_SERVER_URL=https://<huggingface-space>.hf.space
```

- Cloudtype에서는 cloudtype.yaml로 환경 변수를 주입합니다.

---

## 💬 POST /rag

- 법률 질의 처리

#### Request

```
POST /rag
Content-Type: application/json

{
  "query": "건축법상 대수선 기준이 뭐야?"
}
```

#### Response

```
{
  "response": "건축법상 대수선은 내력벽 또는 주요 구조부 변경을 포함하는 공사입니다..."
}
```

---

## ☁ 배포 구조

- Hugging Face Spaces (임베딩 서버)

  - /embed API 제공
  - SentenceTransformer 기반 임베딩 추출

- Cloudtype (RAG API 서버)
  - FastAPI + Uvicorn 기반
  - LLM 호출 및 Qdrant 검색 포함한 LangGraph 실행
