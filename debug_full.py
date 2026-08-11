import sys
import os
import asyncio

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from services.content_generator import generate_content_from_topic
from services.renderer import render_card_news

async def test_full():
    print("Starting full pipeline test with news collector...", flush=True)
    topic = "동물 뉴스"
    try:
        content = generate_content_from_topic(topic)
        print(f"Generated Content Source Name: {content.source_name}", flush=True)
        print(f"Generated Content Source URL: {content.source_url}", flush=True)
        print(f"Category: {content.category}", flush=True)
        print(f"Cover Title: {content.cover.title}", flush=True)
        print(f"Body Slides Count: {len(content.body_slides)}", flush=True)
        
        res = await render_card_news(content, "output/news_test")
        print("SUCCESS! Output images generated count:", len(res), flush=True)
        for path in res:
            print(" - Generated slide image:", path, flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_full())
