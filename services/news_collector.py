import os
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import random

CONTENT_DIR = os.path.abspath("Content")

KOREAN_TO_ENGLISH_SPECIES = {
    "고양이": "cat",
    "강아지": "dog",
    "개": "dog",
    "판다": "panda",
    "곰": "bear",
    "원숭이": "monkey",
    "돌고래": "dolphin",
    "호랑이": "tiger",
    "사자": "lion",
    "상어": "shark",
    "수달": "otter",
    "펭귄": "penguin",
    "악어": "alligator crocodile",
    "코끼리": "elephant",
    "여우": "fox",
    "늑대": "wolf",
    "새": "bird",
    "조류": "bird",
    "돼지": "pig",
    "쥐": "rat mouse",
    "문어": "octopus",
    "캥거루": "kangaroo"
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

HISTORICAL_ANIMAL_STORIES = [
    {
        "title": "호주 맥주 18캔 털어먹고 소와 싸운 엽기 돼지 사건",
        "link": "https://en.wikipedia.org/wiki/Swilling_pig_incident",
        "source": "Daily Mail Global",
        "snippet": "호주 캠핑장에서 관광객의 맥주 18캔을 몰래 따 마시고 취해서 소와 엽기적인 난투극을 벌인 돼지의 충격 실화 사건입니다.",
        "is_historical_fallback": True
    },
    {
        "title": "뉴욕 지하철을 발칵 뒤집은 전설의 '피자 쥐 (Pizza Rat)'",
        "link": "https://en.wikipedia.org/wiki/Pizza_Rat",
        "source": "NY Post Global",
        "snippet": "자신보다 3배 큰 피자 한 조각을 입에 물고 지하철 계단을 당당히 내려가 전 세계 1,000만 뷰를 달성한 뉴욕 엽기 쥐 이야기입니다.",
        "is_historical_fallback": True
    },
    {
        "title": "수족관 배수관 50m 타고 바다로 탈옥한 문어 '인키'",
        "link": "https://en.wikipedia.org/wiki/Inky_(octopus)",
        "source": "BBC World News",
        "snippet": "밤중에 수조 뚜껑을 열고 나와 50m 긴 배수관 파이프를 타고 태평양 바다로 완벽하게 탈옥에 성공한 고지능 문어 인키 실화입니다.",
        "is_historical_fallback": True
    },
    {
        "title": "호주 마을을 무단 점령하고 우체부를 기습한 깡패 캥거루",
        "link": "https://en.wikipedia.org/wiki/Kangaroo",
        "source": "National Geographic",
        "snippet": "근육질 몸매로 마을 주민과 우체부를 무차별 기습하고 마을 하나를 톡톡히 점령했던 호주 엽기 캥거루 사건입니다.",
        "is_historical_fallback": True
    },
    {
        "title": "런던 박물관 지붕에서 거울 보며 춤추는 엽기 여우 발견",
        "link": "https://en.wikipedia.org/wiki/Urban_fox",
        "source": "The Guardian",
        "snippet": "도심 한복판 박물관 지붕 유리에映친 자신의 모습을 보며 춤을 추고 관광객을 유혹한 거침없는 도심 여우 실화입니다.",
        "is_historical_fallback": True
    }
]

def build_search_query(user_query: str) -> str:
    """
    Extracts species and emotion/mood keywords from Korean input and translates them to English Google News query.
    Example: '오싹하고 무서운 고양이 뉴스' -> 'scary terrifying spooky horror cat'
    """
    clean_query = user_query.strip()
    if not clean_query:
        return "bizarre weird animal"

    matched_emotions = []
    for k, v in EMOTION_TO_ENGLISH_MAPPING.items():
        if k in clean_query:
            matched_emotions.append(v)

    matched_species = []
    for k, v in KOREAN_TO_ENGLISH_SPECIES.items():
        if k in clean_query:
            matched_species.append(v)

    raw_words = []
    if matched_emotions:
        for emo in matched_emotions:
            raw_words.extend(emo.split())
    else:
        raw_words.extend(["bizarre", "weird"])

    if matched_species:
        for sp in matched_species:
            raw_words.extend(sp.split())
    else:
        raw_words.append("animal")

    # Deduplicate while preserving order
    seen = set()
    dedup_words = []
    for word in raw_words:
        if word not in seen:
            seen.add(word)
            dedup_words.append(word)

    return " ".join(dedup_words)

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
                except Exception as e:
                    pass
    return used_set

def fetch_real_animal_news(query: str = "") -> dict:
    """
    Fetches fresh, non-duplicate real-time bizarre global animal news from Google News RSS.
    Accurately maps user topic and emotion keywords (e.g. '오싹하고 무서운 고양이') to English RSS queries.
    Prevents generating duplicate news items already present in history.
    """
    existing_used = get_existing_news_identifiers()
    search_term = build_search_query(query)

    try:
        encoded_query = urllib.parse.quote(f"{search_term} news")
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        req = urllib.request.Request(
            rss_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            items = root.findall('.//item')
            if items and len(items) > 0:
                fresh_items = []
                for item in items:
                    link = item.find('link').text if item.find('link') is not None else ""
                    title = item.find('title').text if item.find('title') is not None else ""
                    clean_title = title.rsplit(' - ', 1)[0] if ' - ' in title else title
                    
                    # Deduplication check
                    if link.strip() not in existing_used and clean_title.strip() not in existing_used:
                        fresh_items.append(item)
                
                # Pick a fresh item if available
                candidates = fresh_items if len(fresh_items) > 0 else items
                selected_item = random.choice(candidates[:min(5, len(candidates))])
                
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
        print(f"Global bizarre news fetch error ({e}), switching to historical fallback...", flush=True)

    # Fallback to fresh historical story not yet used
    unused_fallbacks = [story for story in HISTORICAL_ANIMAL_STORIES if story["link"] not in existing_used and story["title"] not in existing_used]
    if len(unused_fallbacks) > 0:
        return random.choice(unused_fallbacks)
        
    return random.choice(HISTORICAL_ANIMAL_STORIES)
