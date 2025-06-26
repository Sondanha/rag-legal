import re
from langchain_core.runnables import RunnableLambda

from typing import Dict, Any, List

BASE_URL = "https://www.law.go.kr"

def parse_llm_response(raw: str) -> Dict[str, Any]:
    """
    LLM 응답에서 answer는 HTML, referenced_laws는 마크다운 리스트로 추출
    """
    # 1. answer / 2. referenced_laws 분리
    sections = re.split(r"\n\s*2\. \*\*referenced_laws\*\*", raw.strip(), maxsplit=1)

    # answer 부분 정리
    answer_section = sections[0].strip()
    answer_match = re.search(r"1\. \*\*answer\*\*\s*(.*)", answer_section, re.DOTALL)
    answer_html = answer_match.group(1).strip() if answer_match else answer_section

    # referenced_laws 부분 정리
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

    parsed = parse_llm_response(raw_response)

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
            "answer": parsed["answer"],  # HTML string
            "referenced_laws": parsed["referenced_laws"],  # markdown list parsed
            "reference_documents": reference_documents
        }
    }

postprocess_reference_documents_runnable = RunnableLambda(postprocess_reference_documents)