import os
import base64
import asyncio
import time
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright
from schemas.content import CardNewsData
from services.image_generator import download_ai_image

def file_to_data_uri(filepath: str) -> str:
    """
    Converts a local file (.jpg, .png, .svg) to a base64 Data URI string.
    This guarantees 100% flawless rendering inside Playwright about:blank context.
    """
    if not os.path.exists(filepath):
        return ""
    ext = os.path.splitext(filepath)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.svg': 'image/svg+xml'
    }
    mime = mime_types.get(ext, 'image/jpeg')
    with open(filepath, 'rb') as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    return f"data:{mime};base64,{encoded}"

def _sync_render_card_news(data: CardNewsData, output_dir: str = "output"):
    """
    Synchronously renders rich CardNewsData into high-quality PNG images using Playwright sync_api.
    Embeds all slide images as Base64 Data URIs to eliminate file path resolution issues in Chromium.
    Inlines style.css directly into template HTML to ensure 100% flawless CSS rendering.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    abs_output_dir = os.path.abspath(output_dir).replace('\\', '/')

    # Read CSS content directly for inline rendering
    css_path = os.path.join('templates', 'style.css')
    css_content = ""
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

    # Setup Jinja2 environment
    env = Environment(loader=FileSystemLoader(['templates', output_dir]))
    template = env.get_template('card_news.html')

    total_slides = len(data.body_slides) + 2  # Cover + N Body + CTA
    category = data.category or "세계동물뉴스"
    source_name = data.source_name or "뉴스 출처"

    print("Pre-downloading AI images for slides...", flush=True)
    
    # Cover image
    cover_target = os.path.join(output_dir, "slide_0_img.jpg")
    cover_actual_path = download_ai_image(data.cover.image_prompt or "dramatic animal story", cover_target)
    cover_data_uri = file_to_data_uri(cover_actual_path)
    time.sleep(1.5) # Gentle pause between AI requests to prevent Pollinations 429
    
    # Body images
    body_data_uris = []
    for i, slide in enumerate(data.body_slides):
        b_target = os.path.join(output_dir, f"slide_{i+1}_img.jpg")
        b_actual_path = download_ai_image(slide.image_prompt or "animal in action", b_target)
        body_data_uris.append(file_to_data_uri(b_actual_path))
        time.sleep(1.5) # Gentle pause

    # CTA image
    cta_target = os.path.join(output_dir, f"slide_{len(data.body_slides)+1}_img.jpg")
    cta_actual_path = download_ai_image(data.cta.image_prompt or "surprised funny animal", cta_target)
    cta_data_uri = file_to_data_uri(cta_actual_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1080, 'height': 1350})

        image_paths = []

        # 1. Render Cover Slide
        cover_html = template.render(
            base_dir=abs_output_dir,
            css_content=css_content,
            slide_type="cover",
            category=category,
            source_name=source_name,
            slide_index="01",
            total_slides=f"{total_slides:02d}",
            tagline=data.cover.tagline or f"😱 {source_name} 엽기 보도",
            title=data.cover.title,
            subtitle=data.cover.subtitle,
            image_path=cover_data_uri
        )
        page.set_content(cover_html, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        cover_path = os.path.join(output_dir, "slide_0_cover.png")
        page.screenshot(path=cover_path)
        image_paths.append(cover_path)

        # 2. Render Body Slides
        for i, slide in enumerate(data.body_slides):
            slide_num = f"{i + 2:02d}"
            body_html = template.render(
                base_dir=abs_output_dir,
                css_content=css_content,
                slide_type="body",
                category=category,
                source_name=source_name,
                slide_index=slide_num,
                total_slides=f"{total_slides:02d}",
                title=slide.title,
                subtitle=slide.subtitle,
                story_text=slide.story_text,
                bullet_points=slide.bullet_points,
                key_tip=slide.key_tip,
                image_path=body_data_uris[i]
            )
            page.set_content(body_html, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            body_path = os.path.join(output_dir, f"slide_{i+1}_body.png")
            page.screenshot(path=body_path)
            image_paths.append(body_path)

        # 3. Render CTA Slide
        cta_num = f"{total_slides:02d}"
        cta_html = template.render(
            base_dir=abs_output_dir,
            css_content=css_content,
            slide_type="cta",
            category=category,
            source_name=source_name,
            slide_index=cta_num,
            total_slides=f"{total_slides:02d}",
            title=data.cta.title,
            content=data.cta.content,
            image_path=cta_data_uri
        )
        page.set_content(cta_html, wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        cta_path = os.path.join(output_dir, f"slide_{len(data.body_slides)+1}_cta.png")
        page.screenshot(path=cta_path)
        image_paths.append(cta_path)

        browser.close()
        return image_paths

async def render_card_news(data: CardNewsData, output_dir: str = "output"):
    """
    Async wrapper executing synchronous Playwright rendering in a worker thread.
    """
    return await asyncio.to_thread(_sync_render_card_news, data, output_dir)
