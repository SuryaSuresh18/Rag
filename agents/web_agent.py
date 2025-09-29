import requests
from bs4 import BeautifulSoup
import hashlib
import os

CACHE_DIR = "cache_web"
os.makedirs(CACHE_DIR, exist_ok=True)

def _cache_key(query: str) -> str:
    return hashlib.md5(query.encode()).hexdigest()

def _load_from_cache(query: str):
    key = _cache_key(query)
    path = os.path.join(CACHE_DIR, f"{key}.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None

def _save_to_cache(query: str, content: str):
    key = _cache_key(query)
    path = os.path.join(CACHE_DIR, f"{key}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def search_web(query: str) -> str:
    cached = _load_from_cache(query)
    if cached:
        print("✅ Loaded web result from cache")
        return cached

    print("🔍 Performing new search using DuckDuckGo Lite")
    url = "https://lite.duckduckgo.com/lite/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.post(url, headers=headers, data={"q": query}, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("a")

        output = ""
        for a in results:
            if a.has_attr("href") and "duckduckgo.com/l/" in a["href"]:
                output += f"{a.get_text()} - {a['href']}\n\n"
            if len(output.splitlines()) > 10:
                break

        _save_to_cache(query, output)
        return output if output else "No relevant results found."
    except Exception as e:
        return f"❌ Web search failed: {e}"
