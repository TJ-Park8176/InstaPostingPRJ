# ************************************************************************
# ** Code Description: Robust Real-Time Animal News Collector with SSL  **
# **                   Support, Strict Species Filtering, and Safe      **
# **                   Deduplication.                                   **
# **                                                                    **
# ** Creator: Origincs / Park.TJ                                        **
# ** Creation Date: 2026.08.17                                          **
# ************************************************************************

import os
import json
import ssl
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import random
from typing import Optional, List, Dict

CONTENT_DIR = os.path.abspath("Content")

KOREAN_TO_ENGLISH_SPECIES = {
    "강아지": ["dog", "puppy", "canine", "hound", "retriever", "poodle", "husky", "bulldog"],
    "개": ["dog", "puppy", "canine", "hound"],
    "고양이": ["cat", "kitten", "feline"],
    "판다": ["panda"],
    "팬더": ["panda"],
    "곰": ["bear", "grizzly"],
    "원숭이": ["monkey", "chimpanzee", "ape", "gorilla"],
    "돌고래": ["dolphin"],
    "고래": ["whale"],
    "호랑이": ["tiger"],
    "사자": ["lion"],
    "상어": ["shark"],
    "수달": ["otter"],
    "펭귄": ["penguin"],
    "악어": ["alligator", "crocodile"],
    "코끼리": ["elephant"],
    "여우": ["fox"],
    "늑대": ["wolf"],
    "새": ["bird", "parrot", "crow", "eagle", "owl"],
    "조류": ["bird"],
    "돼지": ["pig", "piglet"],
    "쥐": ["rat", "mouse", "hamster"],
    "햄스터": ["hamster"],
    "문어": ["octopus"],
    "캥거루": ["kangaroo"],
    "카피바라": ["capybara"],
    "토끼": ["rabbit", "bunny"],
    "너구리": ["raccoon"],
    "라쿤": ["raccoon"],
    "하마": ["hippo", "hippopotamus"],
    "기린": ["giraffe"],
    "바다표범": ["seal", "sea lion"],
    "물개": ["seal", "sea lion"]
}

EMOTION_TO_ENGLISH_MAPPING = {
    "오싹": "scary terrifying spooky",
    "무서운": "scary terrifying horror",
    "무서": "scary terrifying",
    "섬뜩": "creepy spooky eerie",
    "공포": "horror scary terrifying",
    "괴기": "eerie weird uncanny",
    "귀여운": "cute adorable heartwarming",
    "귀여": "cute adorable",
    "아기": "baby cute adorable",
    "사랑스러운": "lovely adorable heartwarming",
    "심쿵": "cute heart-melting adorable",
    "엽기": "bizarre weird strange",
    "황당": "bizarre absurd ridiculous",
    "웃긴": "funny hilarious comedic",
    "감동": "touching heartwarming hero rescue",
    "눈물": "emotional touching tearjerker",
    "구조": "heroic rescue saved",
    "구한": "rescue saved hero",
    "신비": "mysterious magical rare",
    "놀라운": "amazing astonishing incredible",
    "희귀": "rare unusual exotic",
    "거대": "giant massive huge monstrous"
}

def get_target_species_keywords(user_query: str) -> List[str]:
    """Extracts target English species keywords corresponding to the Korean user query."""
    clean_query = user_query.strip()
    target_keywords = []
    for k, keywords in KOREAN_TO_ENGLISH_SPECIES.items():
        if k in clean_query:
            target_keywords.extend(keywords)
    return list(dict.fromkeys(target_keywords))

def build_search_query(user_query: str) -> str:
    """
    Builds a precise Google News search query prioritizing the user's requested animal.
    Example: '강아지' -> 'dog'
    Example: '오싹하고 무서운 고양이 뉴스' -> 'scary cat'
    """
    clean_query = user_query.strip()
    if not clean_query:
        return "bizarre animal"

    matched_emotions = []
    for k, v in EMOTION_TO_ENGLISH_MAPPING.items():
        if k in clean_query:
            matched_emotions.append(v.split()[0]) # Pick primary emotion keyword

    target_species = get_target_species_keywords(clean_query)

    query_parts = []
    if matched_emotions:
        query_parts.append(matched_emotions[0])
    if target_species:
        query_parts.append(target_species[0]) # e.g. 'dog'
    else:
        # Fallback to general animal if no specific species was typed
        query_parts.append("animal")

    return " ".join(query_parts)

def get_existing_news_identifiers() -> set:
    """Collects titles and URLs of already generated card news from Content/ folder."""
    used_set = set()
    if os.path.exists(CONTENT_DIR):
        for folder in os.listdir(CONTENT_DIR):
            meta_path = os.path.join(CONTENT_DIR, folder, "meta.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        if "content" in meta:
                            if meta["content"].get("source_url"):
                                used_set.add(meta["content"]["source_url"].strip())
                            if meta["content"].get("cover_slide", {}).get("title"):
                                used_set.add(meta["content"]["cover_slide"]["title"].strip())
                        if meta.get("source_url"):
                            used_set.add(meta["source_url"].strip())
                except Exception:
                    pass
    return used_set

def fetch_real_animal_news(query: str = "") -> Optional[Dict]:
    """
    Fetches fresh, non-duplicate animal news from Google News RSS with strict species verification.
    Uses unverified SSL context to prevent macOS certificate verification failures.
    Returns None if no matching verified news is found, allowing LLM dynamic factual fallback.
    """
    existing_used = get_existing_news_identifiers()
    search_term = build_search_query(query)
    target_species = get_target_species_keywords(query)

    # SSL Context bypassing certificate check (fixes macOS urllib error)
    ssl_context = ssl._create_unverified_context()

    try:
        encoded_query = urllib.parse.quote(f"{search_term} news")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        req = urllib.request.Request(
            rss_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=8, context=ssl_context) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            items = root.findall('.//item')
            if items and len(items) > 0:
                verified_items = []
                for item in items:
                    link = item.find('link').text if item.find('link') is not None else ""
                    title = item.find('title').text if item.find('title') is not None else ""
                    desc = item.find('description').text if item.find('description') is not None else ""
                    clean_title = title.rsplit(' - ', 1)[0] if ' - ' in title else title
                    
                    # Deduplication check
                    if link.strip() in existing_used or clean_title.strip() in existing_used:
                        continue

                    # Strict species filtering if user specified an animal
                    if target_species:
                        combined_text = f"{clean_title} {desc}".lower()
                        if not any(sp in combined_text for sp in target_species):
                            continue # Skip non-matching animal news

                    verified_items.append(item)
                
                if verified_items:
                    selected_item = random.choice(verified_items[:min(5, len(verified_items))])
                    title = selected_item.find('title').text if selected_item.find('title') is not None else ""
                    link = selected_item.find('link').text if selected_item.find('link') is not None else ""
                    pubDate = selected_item.find('pubDate').text if selected_item.find('pubDate') is not None else ""
                    source_elem = selected_item.find('source')
                    source = source_elem.text if source_elem is not None and source_elem.text else "Global News"
                    clean_title = title.rsplit(' - ', 1)[0] if ' - ' in title else title
                    
                    return {
                        "title": clean_title,
                        "link": link,
                        "source": source,
                        "pubDate": pubDate,
                        "snippet": clean_title,
                        "is_historical_fallback": False
                    }
    except Exception as e:
        print(f"Notice: Google News RSS fetch notice ({e}). Switching to dynamic factual discovery...", flush=True)

    # Return None if no RSS item passed strict verification, triggering dynamic factual LLM generation
    return None
