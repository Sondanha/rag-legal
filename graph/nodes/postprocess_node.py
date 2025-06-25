import re
from typing import Dict, Any, List
from langchain_core.runnables import RunnableLambda

BASE_URL = "https://www.law.go.kr"

def parse_llm_response(raw: str) -> Dict[str, Any]:
    
    print("=== RAW RESPONSE START ===")
    print(raw)
    print("=== RAW RESPONSE END ===")
    
    sections = re.split(r'\n(?=\d\. \*\*.+?\*\*)', raw.strip())
    print("=== PARSED SECTIONS ===")
    print(sections)
    result = {"answer": "", "referenced_laws": []}


    for section in sections:
        match = re.match(r'^(\d+)\. \*\*(.+?)\*\*\n', section)
        if not match:
            continue

        key = match.group(2).strip().lower().replace(" ", "_")
        content = section[match.end():].strip()

        if key == "answer":
            result["answer"] = content

        elif key == "referenced_laws":
            result["referenced_laws"] = [
                line.lstrip("* ").strip()
                for line in content.splitlines()
                if line.strip()
            ]

    return result


def postprocess_reference_documents(state: Any) -> Dict[str, Any]:
    if isinstance(state, str):
        state = {"response": state}

    raw_response = state.get("response", "")
    law_docs = state.get("law_docs", [])
    ordin_docs = state.get("ordin_docs", [])

    parsed = parse_llm_response(raw_response if isinstance(raw_response, str) else "")

    reference_documents = []
    seen_urls = set()  # ✅ 중복 제거: URL 기준

    for doc in law_docs + ordin_docs:
        number = doc.get("number")
        title_base = doc.get("title", "알 수 없는 조문")
        table_title = doc.get("table_title", "").strip()
        pdf_path = doc.get("table_pdf", "").strip()

        if not pdf_path or not number:
            continue

        full_url = f"{BASE_URL}{pdf_path}"
        if full_url in seen_urls:
            continue  # ✅ 이미 추가된 URL은 무시
        seen_urls.add(full_url)

        if table_title:
            title = f"{title_base} ({number}) - {table_title}"
        else:
            title = f"{title_base} ({number})"

        reference_documents.append({
            "title": title,
            "url": full_url
        })

    return {
        **state,
        "response": {
            "answer": parsed["answer"],
            "referenced_laws": parsed["referenced_laws"],
            "reference_documents": reference_documents
        }
    }

postprocess_reference_documents_runnable = RunnableLambda(postprocess_reference_documents)
