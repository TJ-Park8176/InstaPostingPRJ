# 🐾 InstaPostingPRJ - 인스타그램 AI 동물 카드뉴스 자동 생성기

**InstaPostingPRJ**는 실시간 해외 동물 소식(구글 뉴스 RSS) 및 사용자 입력을 기반으로, **Google Gemini 3.5 Flash** 및 **Nano Banana 2 (`gemini-3.1-flash-image`) AI**를 활용하여 초고화질 1080x1080 풀블리드 에디토리얼 인스타그램 카드뉴스를 자동 제작하고 영구 보관하는 파이썬 웹 애플리케이션입니다.

---

## 🌟 주요 기능 (Key Features)

1. **📰 실시간 뉴스 수집 & 중복 방지 (News Collector)**:
   - 구글 뉴스 RSS 실시간 파싱 및 감정/분위기 키워드("오싹", "무서운", "귀여운", "감동") 자동 번역 쿼리 빌더.
   - `Content/` 보관함 내 `meta.json` 이력을 스캔하여 이미 제작한 뉴스는 자동 스킵(Deduplication).

2. **📖 단일 실화 완결형 서사 (4-Act Narrative Arc Storytelling)**:
   - 떡밥성 낚시 헤드라인을 배제하고, 단 하나의 실화 사건에 대해 **기승전결(발단-전개-반전-결말)**이 명확한 1.5줄 완결성 문구 및 클리프행어 제공.

3. **🎨 100% Full-Bleed 미디어 레이아웃 & 최적화 브랜딩**:
   - 풀스크린 HD 이미지 + 비브런트 코랄 레드 & 골드 엠버 시그니처 브랜딩.
   - 배경 이미지가 80% 이상 시원하게 드러나도록 40px 스토리 폰트 및 슬림 페이드 최적화.

4. **📂 Content 영구 보관함 & 미리보기 모달**:
   - `Content/post_{id}_{timestamp}/` 폴더 자동 저장.
   - 라이트박스(Lightbox) 대형 미리보기, 캡션 1초 복사, ZIP 전체 다운로드 지원.

---

## 🛠️ 기술 스택 (Tech Stack)

- **Backend**: Python 3.9+, FastAPI, Playwright, Jinja2
- **AI Models**:
  - LLM: `gemini-3.5-flash` (스토리 기획 및 캡션 작성)
  - Image Gen: `gemini-3.1-flash-image` (Nano Banana 2 고화질 1080x1080 이미지 생성)
- **Frontend**: HTML5, CSS3, Vanilla JS

---

## 🚀 실행 방법 (Getting Started)

### 🍎 맥북(macOS) 1-Click 자동 설치 & 1초 실행 (MacBook)

1. **최초 1회 자동 인스톨 (터미널)**:
   ```bash
   chmod +x setup_mac.sh start_mac.command
   ./setup_mac.sh
   ```
2. **이후 사용 시 (더블 클릭 1초 실행)**:
   - 맥 파인더(Finder)에서 **`start_mac.command`** 아이콘을 더블 클릭합니다.
   - 터미널 서비스가 시작되고, **웹 브라우저(`http://localhost:8000`)가 자동으로 오픈**됩니다!

---

### 💻 윈도우(Windows) 및 일반 환경

1. **의존성 라이브러리 설치**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **환경변수 설정 (`.env`)**:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **웹 애플리케이션 구동**:
   ```bash
   python main.py
   ```
   브라우저에서 `http://localhost:8000` 접속.
