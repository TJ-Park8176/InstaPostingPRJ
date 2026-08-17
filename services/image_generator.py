import os
import time
import random
import urllib.request
import urllib.parse
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# Recommended Nano Banana models in order of priority
NANO_BANANA_MODELS = [
    "gemini-3.1-flash-image",      # Nano Banana 2 (Super fast & high quality)
    "gemini-2.5-flash-image",      # Nano Banana (Standard)
    "gemini-3-pro-image",          # Nano Banana Pro (Ultra high quality)
]

def download_ai_image(prompt: str, save_filepath: str) -> str:
    """
    Generates high-quality AI images using Google's native Nano Banana (Gemini Image Generation) models.
    Falls back to Pollinations AI / HD photos / local SVG if needed.
    """
    os.makedirs(os.path.dirname(save_filepath), exist_ok=True)

    # 1. Try Nano Banana (Gemini Native Image Generation)
    if api_key:
        for model_name in NANO_BANANA_MODELS:
            try:
                print(f"Generating AI image via {model_name} for prompt: '{prompt[:40]}...' to {save_filepath}", flush=True)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                
                if hasattr(response, 'parts'):
                    for part in response.parts:
                        inline_data = getattr(part, 'inline_data', None)
                        if inline_data and hasattr(inline_data, 'data'):
                            with open(save_filepath, 'wb') as f:
                                f.write(inline_data.data)
                            print(f"SUCCESS! AI image generated via {model_name}", flush=True)
                            return save_filepath
            except Exception as e:
                print(f"Notice: {model_name} image generation notice ({e}), trying next option...", flush=True)

    # 2. Try Pollinations AI fallback
    try:
        short_prompt = prompt.strip().split('.')[0][:60]
        clean_prompt = urllib.parse.quote(short_prompt)
        pollinations_url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1350&seed={random.randint(1, 99999)}&nologo=true"
        
        req = urllib.request.Request(
            pollinations_url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status == 200:
                content = response.read()
                if len(content) > 5000:
                    with open(save_filepath, 'wb') as f:
                        f.write(content)
                    return save_filepath
    except Exception as e:
        print(f"Pollinations AI fallback notice ({e})...", flush=True)

    # 3. Local Styled SVG Fallback (1080 x 1350 Vertical 4:5)
    fallback_path = save_filepath.replace(".jpg", ".svg").replace(".png", ".svg")
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">
      <defs>
        <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" style="stop-color:#1e293b;stop-opacity:1" />
          <stop offset="50%" style="stop-color:#0f172a;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#3b0764;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="badgeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" style="stop-color:#ff4b4b;stop-opacity:1" />
          <stop offset="100%" style="stop-color:#ff8533;stop-opacity:1" />
        </linearGradient>
      </defs>
      <rect width="1080" height="1350" fill="url(#bgGrad)"/>
      <circle cx="540" cy="500" r="140" fill="#ffffff" fill-opacity="0.05" stroke="#ffffff" stroke-opacity="0.1" stroke-width="3"/>
      <text x="540" y="540" font-family="'Pretendard', sans-serif" font-size="120" text-anchor="middle">🦁</text>
      <rect x="340" y="700" width="400" height="56" fill="url(#badgeGrad)" rx="28"/>
      <text x="540" y="736" font-family="'Pretendard', sans-serif" font-size="24" fill="#ffffff" text-anchor="middle" font-weight="bold">WORLD BIZARRE ANIMAL</text>
      <text x="540" y="820" font-family="'Pretendard', sans-serif" font-size="22" fill="#94a3b8" text-anchor="middle">Real News Story Illustration (1080x1350)</text>
    </svg>"""
    
    with open(fallback_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
        
    return fallback_path
