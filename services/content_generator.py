import os
import time
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from schemas.content import CardNewsData
from services.news_collector import fetch_real_animal_news
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

MODELS_TO_TRY = ["gemini-3.5-flash"]

SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

def generate_content_from_topic(topic: str) -> CardNewsData:
    """
    Generates single-narrative complete (기승전결 4-act) Instagram Card News based on a real bizarre global animal news story.
    Enforces telling ONE complete story with an engaging beginning, development, climax twist, and definitive conclusion.
    """
    news_item = fetch_real_animal_news(topic)
    
    source_name = news_item["source"]
    source_url = news_item["link"]
    is_fallback = news_item["is_historical_fallback"]
    news_title = news_item["title"]
    news_snippet = news_item["snippet"]

    prompt = f"""
    [해외 엽기/놀라운 동물 실화 기사 정보]
    - 기사 제목: {news_title}
    - 언론사 출처: {source_name}
    - 원문 링크: {source_url}
    - 기사 요약: {news_snippet}

    위 뉴스 기사는 **단 하나의 실제 사건 스토리**입니다.
    이 기사 속에 담긴 하나의 사건에 대해 **처음부터 결말까지 완벽한 기승전결(4-Act Narrative Storytelling)** 구조로 총 6장의 인스타그램 카드뉴스를 작성하세요.

    [핵심 작성 지침 - 1.5줄 요약 & 호기심 클리프행어]
    1. **단일 사건 완결형 4단계 서사 구조**:
       - **슬라이드 1 (기: 사건의 발단)**: 평화롭던 장소에서 벌어진 의문의 사건 시작 및 최초 목격.
       - **슬라이드 2 (승: 사건의 전개/위기)**: 예상치 못한 엽기적/극적인 사건의 확대와 사람들의 당황하는 전개.
       - **슬라이드 3 (전: 반전 & 클라이맥스)**: 의외의 범인(동물)이나 기발한 반전이 드러나는 피크 절정 순간.
       - **슬라이드 4 (결: 명확한 최종 결말 & 후일담)**: 결론을 확실하게 내리고, 동물의 결말과 훈훈한 후일담 마무리.
    2. **1.5줄 간결한 문구 & 클리프행어(다음 장 궁금증 유발)**:
       - 각 슬라이드의 `story_text`는 **최대 60자 이내 (1.5줄 이내)**로 핵심만 매우 간결하게 축약하세요.
       - 텍스트가 배경 이미지를 많이 가리지 않도록 2문장 이내로 작성하고, 슬라이드 끝부분은 다음 장이 궁금해지는 질문이나 반전 복선을 포함하세요! (예: "과연 녀석의 진짜 정체는?", "그런데 믿기 힘든 반전이 시작됩니다.")
       - `subtitle` 및 `key_tip`은 빈 문자열(`""`), `bullet_points`는 빈 배열(`[]`)로 작성하세요.
    3. **이미지 프롬프트 지침**:
       - 사건의 4단계 서사에 부합하는 고화질 비주얼 스타일을 영어로 작성하세요. (실사 photorealistic 또는 3D cartoon 명시)

    [필수 JSON 응답 구조]
    {{
      "category": "세계엽기동물",
      "source_name": "{source_name}",
      "source_url": "{source_url}",
      "is_historical_fallback": {str(is_fallback).lower()},
      "cover": {{
        "tagline": "📌 {source_name} 엽기 실화",
        "title": "단 하나의 사건을 대변하는 강렬한 1줄 제목",
        "subtitle": "궁금증을 자아내는 핵심 1줄 서머리",
        "image_prompt": "English image prompt for cover slide"
      }},
      "body_slides": [
        {{
          "title": "사건의 발단: 이상 현상 발생",
          "subtitle": "",
          "story_text": "사건 시작 배경과 궁금증을 유발하는 1.5줄 문장 (60자 이내).",
          "bullet_points": [],
          "key_tip": "",
          "image_prompt": "English image prompt for slide 1"
        }},
        {{
          "title": "사건의 전개: 당황스러운 혼란",
          "subtitle": "",
          "story_text": "사건 확대 상황과 다음 반전을 기대하게 하는 1.5줄 문장 (60자 이내).",
          "bullet_points": [],
          "key_tip": "",
          "image_prompt": "English image prompt for slide 2"
        }},
        {{
          "title": "결정적 반전: 범인의 실체",
          "subtitle": "",
          "story_text": "의외의 범인과 충격 반전을 포착한 1.5줄 문장 (60자 이내).",
          "bullet_points": [],
          "key_tip": "",
          "image_prompt": "English image prompt for slide 3"
        }},
        {{
          "title": "최종 결말: 훈훈한 후일담",
          "subtitle": "",
          "story_text": "사건의 확실한 명확 결말과 훈훈한 1.5줄 후일담 (60자 이내).",
          "bullet_points": [],
          "key_tip": "",
          "image_prompt": "English image prompt for slide 4"
        }}
      ],
      "cta": {{
        "title": "놀라운 실화 잘 보셨나요? 😱",
        "content": "팔로우하고 매일 새로운 세계 동물 실화를 만나보세요!",
        "image_prompt": "English image prompt for CTA slide"
      }},
      "caption": "인스타그램 게시글 본문 (전말 스토리 요약 및 출처 명시)",
      "hashtags": ["#세계동물뉴스", "#해외이슈", "#엽기동물", "#동물실화", "#카드뉴스"]
    }}
    """

    last_error = None
    for attempt in range(3):
        for model_name in MODELS_TO_TRY:
            try:
                model = genai.GenerativeModel(
                    model_name=model_name,
                    generation_config={
                        "response_mime_type": "application/json",
                        "temperature": 0.7,
                    },
                    safety_settings=SAFETY_SETTINGS
                )
                response = model.generate_content(prompt)
                
                # Strip markdown json codeblock if present
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()

                return CardNewsData.model_validate_json(raw_text)
            except Exception as e:
                print(f"Model {model_name} attempt {attempt+1} failed ({e}), waiting 3s...", flush=True)
                last_error = e
                time.sleep(3)

    raise last_error
