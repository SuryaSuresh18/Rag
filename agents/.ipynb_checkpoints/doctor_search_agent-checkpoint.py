import os
import re
import json
import hashlib
import time

from playwright.async_api import async_playwright
import asyncio
CACHE_DIR = "cache_doctor"
os.makedirs(CACHE_DIR, exist_ok=True)


def _doctor_cache_key(role, city):
    key = f"{role}_{city}".lower().strip()
    return hashlib.md5(key.encode()).hexdigest()


def _load_doctor_cache(role, city):
    key = _doctor_cache_key(role, city)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def _save_doctor_cache(role, city, data):
    key = _doctor_cache_key(role, city)
    cache_file = os.path.join(CACHE_DIR, f"{key}.json")
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

async def search_doctor(city, specialty):
    role = specialty.lower().strip()
    city = city.lower().strip()
    search_url = f"https://www.practo.com/search?results_for=doctor&query={role}&city={city}"

    cached = _load_doctor_cache(role, city)
    if cached:
        return f"✅ Loaded cached results for {role} in {city}\n\n" + "\n".join(cached)

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(search_url)
        await page.wait_for_timeout(5000)

        try:
            cards = page.locator('div[data-qa-id="doctor_card"]')
            count = await cards.count()
            for i in range(min(count, 5)):
                card = cards.nth(i)
                name = await card.locator('h2').inner_text()
                doc_specialty = await card.locator('p:below(h2)').first.inner_text()
                location = await card.locator('div:has-text("Location")').first.inner_text()
                link = await card.locator('a').first.get_attribute("href")
                results.append(f"{i+1}. **{name}** — {doc_specialty}\n📍 {location}\n🔗 {link}")
        except Exception as e:
            results.append(f"❌ Failed to extract doctor cards: {e}")

        await browser.close()

    if not results:
        results.append(f"❌ No verified {role} found. [Search manually]({search_url})")

    _save_doctor_cache(role, city, results)
    return "\n".join(results)

def summarize_doctor_results(doctor_list, role):
    summary = []
    for entry in doctor_list:
        if "**" in entry and "📍" in entry:
            summary.append(entry.split("\n")[0])  # Only name + specialty
    return summary

async def search_doctor_info(specialties: list, location: str, use_cache=True) -> dict:

    location = location.lower().strip()
    result = {}

    print("🔍 Performing doctor search using Playwright...")

    for specialty in specialties:
        role = specialty.lower().strip()

        doctor_data = None
        if use_cache:
            doctor_data = _load_doctor_cache(role, location)

        if doctor_data:
            print(f"✅ Loaded cached results for {role} in {location}")
        else:
            # Perform fresh search
            raw_result = await search_doctor(location, role)

            doctor_data = raw_result.split('\n')
            _save_doctor_cache(role, location, doctor_data)

        # Check if any actual doctors were found
        found_doctors = summarize_doctor_results(doctor_data, role)
        if found_doctors:
            print(f"✅ {specialty.title()} → Found {len(found_doctors)} doctors")
            result[specialty] = found_doctors
        else:
            print(f"❌ {specialty.title()} → Not found")
            search_url = f"https://www.practo.com/search?results_for=doctor&query={role}&city={location}"
            result[specialty] = [f"❌ No verified {specialty.title()} found. [Search manually]({search_url})"]

    return result



# === Similarity Matcher ===
def _is_similar(a: str, b: str) -> bool:
    ratio = SequenceMatcher(None, a.lower(), b.lower()).ratio()
    print(f"🧼 Similarity ratio between '{a}' and '{b}': {ratio:.2f}")
    return ratio > 0.5

# === Extract Roles from Diagnosis ===
def get_doctor_specialty(diagnosis: str, rag_chain) -> list:
    followup = f"Based on the diagnosis: '{diagnosis}', what kind of medical specialists should be consulted?"
    response = rag_chain.invoke(followup)["result"]
    print("🧠 RAG Response:\n", response)

    known_roles = [
        "pediatrician", "neurologist", "psychologist", "psychiatrist",
        "speech-language pathologist", "speech therapist",
        "behavioral specialist", "psychotherapist", "counselor", "therapist"
    ]

    found_roles = set()
    for role in known_roles:
        if re.search(rf"\b{re.escape(role)}\b", response.lower()):
            found_roles.add(role)

    print("✅ Extracted Roles:", found_roles)
    return list(found_roles)

# === Normalize Role Names ===
def normalize_roles(roles: list) -> list:
    mapping = {
        "child psychologist": "psychologist",
        "clinical psychologist": "psychologist",
        "pediatrician": "pediatrician",
        "neurologist": "neurologist",
        "behavioral specialist": "psychologist",
        "psychotherapist": "psychologist"
    }
    return list(set([mapping.get(role.lower(), role.title()) for role in roles]))

def search_multiple_doctors(roles, city):
    city = city.lower().strip()
    normalized_roles = [role.title() for role in roles]
    query_string = ",".join(sorted(set(normalized_roles)))
    search_url = f"https://www.practo.com/search?results_for=doctor&query={query_string}&city={city}"
    
    return f"❌ No verified {', '.join(normalized_roles)} found. [Search manually]({search_url})"


# === Doctor Search from Practo using Selenium ===

