import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
assert api_key, "GOOGLE_API_KEY is not set in .env"

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-1.5-flash")

def call_llm(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"[LLM 호출 실패] {e}"
