# agents/summarizer_agent.py
from langchain_community.llms import Ollama
from config import MODEL_NAME

llm = Ollama(model=MODEL_NAME)

def summarize_text(text: str) -> str:
    prompt = f"Summarize the following information in simple terms suitable for an email:\n{text}"
    return llm.invoke(prompt)
