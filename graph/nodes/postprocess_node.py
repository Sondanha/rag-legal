import re
import os
from typing import Dict, Any, List
from langchain_core.runnables import RunnableLambda

BASE_URL = "https://www.law.go.kr"

def parse_llm_response(raw: str) -> Dict[str, Any]:
    sections = re.split(r"\n\s*2\. \*\*referenced_laws\*\*", raw.strip(), maxsplit=1)

    answer_section = sections[0].strip()
    answer_match = re.search(r"1\. \*\*answer\*\*\s*(.*)", answer_section, re.DOTALL)
    answer_html = answer_match.group(1).strip() if answer_match else answer_section

    referenced_laws_section = sections[1].strip() if len(sections) > 1 else ""
    referenced_laws = [
        line.lstrip("* ").strip()
        for line in referenced_laws_section.splitlines()
        if line.strip().startswith("*")
    ]

    return {
        "answer": answer_html,
        "referenced_laws": referenced_laws
    }

def postprocess_reference_documents(state: Any) -> Dict[str, Any]:
    if isinstance(state, str):
        state = {"response": state}

    raw_response = state.get("response", "")
    law_docs = state.get("law_docs", [])
    ordin_docs = state.get("ordin_docs", [])
    query = state.get("query", "")

    parsed = parse_llm_response(raw_response)

    map_pattern = re.compile(r"(상권\s*분석|상권분석|지도|보완\s*업종|보완업종|근처|유사업종)", re.IGNORECASE)
    if map_pattern.search(query):
        map_url = os.environ.get("MAP_PAGE_URL", "https://localhost:3000/map")
        tool_message = (
            f"<div style='margin-top: 1rem;'>"
            f"📍 주변 상권과 용도 지역을 <a href='{map_url}' target='_blank'>지도 페이지</a>에서 확인하실 수 있어요."
            f"</div>"
        )
        parsed["answer"] += tool_message

    reference_documents = []
    seen_urls = set()

    for doc in law_docs + ordin_docs:
        number = doc.get("number")
        title_base = doc.get("title", "알 수 없는 조문")
        table_title = doc.get("table_title", "").strip()
        pdf_path = doc.get("table_pdf", "").strip()

        if not pdf_path or not number:
            continue

        full_url = f"{BASE_URL}{pdf_path}"
        if full_url in seen_urls:
            continue
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
