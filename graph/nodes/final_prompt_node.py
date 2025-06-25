from langchain_core.runnables import RunnableLambda
from textwrap import dedent

# 🔹 코드 → 법명 매핑
LAW_CODE_TO_NAME = {
    "BLD": "건축법",
    "FOOD": "식품위생법",
    "PUBH": "공중위생법",
    "LOCL": "지방자치법"
}

# 🔹 강남구 동 리스트
GANGNAM_DONGS = [
    "신사동", "논현동", "압구정동", "청담동", "삼성동", "대치동", "역삼동",
    "도곡동", "개포동", "세곡동", "일원동", "수서동"
]

def build_final_prompt(state: dict) -> dict:
    query = state.get("query", "").strip()

    # 프롬프트 하단에 삽입될 답변 지침
    instructions = dedent("""
    📌 답변 작성 지침:
    - 당신은 법률 전문가이며, 법률 지식이 없는 일반인을 대상으로 쉽게 설명해야 합니다.
    - 어려운 법률 용어나 문장은 일상적인 표현으로 풀어 써 주세요. 예를 들어, ‘의무’는 ‘해야 할 일’, ‘처분’은 ‘결정하거나 조치하는 것’처럼 설명합니다.
    - "문서를 참고하세요", "문서에 명시되어 있지 않습니다" 같은 표현은 피하고, 주어진 문서에서 유의미한 정보를 직접 찾아 답변에 녹여내야 합니다.
    - "다른 법률을 참고하세요" 같은 일반적인 권고는 삼가고, 지금 제공된 조례나 법령 등의 문서 안에서 실질적인 도움을 줄 수 있는 내용을 우선적으로 전달하십시오.
    - 질문자의 상황에 직접적으로 도움이 되는 핵심 내용을 요점부터 설명하고, 필요시 간단한 예시나 상황을 들어 설명해 주세요.
    - 답변은 **마크다운이 아닌 HTML 형식으로만 작성**해 주세요.
        - `<p>` 태그로 문단 구분
        - `<strong>` 또는 `<span style="font-weight:600">` 으로 강조
        - `<h3>`로 소제목 처리
        - 줄바꿈은 `<br>` 대신 문단 구분으로 표현

    ❗ 마크다운(Markdown)은 절대 사용하지 마세요.

    ✏️ 출력 예시:
        1. **answer**
        <p>...</p> <p><strong>중요 사항:</strong> ...</p>
        
        2. **referenced_laws**
        * 법 이름 조항
        * ...
""")

    # 조례
    ordin_context = "\n\n".join([doc.get("text", "") for doc in state.get("ordin_docs", [])])

    # 법령
    law_context_list = []
    for doc in state.get("law_docs", []):
        raw_code = doc.get("law_group", "")
        law_name = LAW_CODE_TO_NAME.get(raw_code, raw_code)

        summary = f"{law_name} {doc.get('number', '')}조 {doc.get('title', '')}\n{doc.get('text', '')}"
        law_context_list.append(summary)
    law_context = "\n\n".join(law_context_list)

    # 전화번호
    number_docs = state.get("number_docs", [])
    number_context = "\n\n".join([
        f"{doc.get('부서명', '')} {doc.get('이름', '')} ({doc.get('직책', '')}): {doc.get('업무내용', '')} ☎ {doc.get('전화번호', '')}"
        for doc in number_docs
    ])

    # 지역명이 명시되지 않았는가?
    region_specified = any(dong in query for dong in GANGNAM_DONGS)

    # 전화번호 섹션
    number_section = ""
    if number_context:
        number_section = f"[전화번호 참고문서]\n{number_context}"
    elif not region_specified:
        number_section = "※ 참고: 동 이름(예: 신사동, 대치동 등)을 알려주시면 더 정확한 연락처를 제공해드릴 수 있습니다."

    # 문서 섹션 조합
    sections = [s for s in [
        f"[조례 참고문서]\n{ordin_context}" if ordin_context else "",
        f"[법령 참고문서]\n{law_context}" if law_context else "",
        number_section
    ] if s]

    reference_sections = "\n\n".join(sections)

    # 최종 프롬프트 구성
    full_prompt = (
        f"다음은 사용자의 질문과 관련된 문서들입니다.\n\n"
        f"{reference_sections}\n\n"
        f"이 문서들을 참고하여 아래 질문에 정확하게 답하세요:\n\n"
        f"질문: {query}\n\n"
        f"{instructions.strip()}"
    )

    return {
        **state,
        "prompt": full_prompt.strip()
    }

final_prompt_runnable = RunnableLambda(build_final_prompt)