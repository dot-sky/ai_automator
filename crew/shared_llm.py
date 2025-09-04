from crewai import LLM

from config.settings import GEMINI_API_KEY


def get_gemini_llm():
    return LLM(
        model='gemini/gemini-2.5-flash',
        api_key=GEMINI_API_KEY,
        temperature=0.0
    )
