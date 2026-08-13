import os
import sys
import asyncio
import json
import shutil
from datetime import datetime

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.database import engine, Base, get_db
from models.post import Post, PostStatus
from services.content_generator import generate_content_from_topic
from services.renderer import render_card_news

Base.metadata.create_all(bind=engine)

app = FastAPI(title="InstaPostingPRJ Web UI")

# Ensure output & Content directories exist
CONTENT_DIR = os.path.abspath("Content")
OUTPUT_DIR = os.path.abspath("output")

os.makedirs(CONTENT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Mount output & Content directories so images can be served to the browser
app.mount("/output", StaticFiles(directory=OUTPUT_DIR), name="output")
app.mount("/Content", StaticFiles(directory=CONTENT_DIR), name="Content")

from schemas.feedback import CardNewsFeedback

# Setup Jinja2 templates for the Web UI
templates = Jinja2Templates(directory="templates")

FEEDBACK_FILE = os.path.join(CONTENT_DIR, "feedbacks.json")

def load_all_feedbacks():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    try:
        with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading feedbacks: {e}")
        return []

def save_feedback_entry(fb_dict: dict):
    feedbacks = load_all_feedbacks()
    # Replace existing feedback for same post_id if present
    feedbacks = [f for f in feedbacks if str(f.get("post_id")) != str(fb_dict.get("post_id"))]
    feedbacks.append(fb_dict)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)

@app.post("/api/feedback")
async def save_feedback(fb: CardNewsFeedback):
    try:
        fb_data = fb.model_dump()
        fb_data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fb_data["overall_score"] = fb.overall_score
        save_feedback_entry(fb_data)
        
        # Also update meta.json inside Content/ if folder exists
        for item in os.listdir(CONTENT_DIR):
            item_path = os.path.join(CONTENT_DIR, item)
            if os.path.isdir(item_path):
                meta_file = os.path.join(item_path, "meta.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        if str(meta.get("post_id")) == str(fb.post_id) or str(meta.get("folder_name")) == str(fb.post_id):
                            meta["feedback"] = fb_data
                            with open(meta_file, "w", encoding="utf-8") as f:
                                json.dump(meta, f, ensure_ascii=False, indent=2)
                    except Exception:
                        pass
        return {"status": "success", "data": fb_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/feedback/{post_id}")
async def get_feedback(post_id: str):
    feedbacks = load_all_feedbacks()
    for fb in feedbacks:
        if str(fb.get("post_id")) == str(post_id):
            return {"status": "success", "data": fb}
    return {"status": "not_found", "data": None}

# Web UI Route
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

class GenerateAndRenderRequest(BaseModel):
    topic: str

@app.post("/api/content/generate_and_render")
async def generate_and_render_content(req: GenerateAndRenderRequest, db: Session = Depends(get_db)):
    try:
        # 1. Generate content via LLM
        card_data = generate_content_from_topic(req.topic)
        
        # 2. Save draft to DB
        new_post = Post(
            topic=req.topic,
            status=PostStatus.DRAFT,
            content_json=card_data.model_dump_json(),
            caption=card_data.caption
        )
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        # 3. Render Images to output directory
        output_sub_dir = f"output/post_{new_post.id}"
        image_paths = await render_card_news(card_data, output_dir=output_sub_dir)
        
        # 4. Save persistent copy to C:\Users\ptj81\Documents\Antygravity\InstaPostingPRJ\Content
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_folder_name = f"post_{new_post.id}_{timestamp_str}"
        content_post_dir = os.path.join(CONTENT_DIR, content_folder_name)
        os.makedirs(content_post_dir, exist_ok=True)
        
        content_image_paths = []
        for img_path in image_paths:
            if os.path.exists(img_path):
                file_name = os.path.basename(img_path)
                dest_path = os.path.join(content_post_dir, file_name)
                shutil.copy2(img_path, dest_path)
                # Store web-accessible relative URL
                content_image_paths.append(f"Content/{content_folder_name}/{file_name}")

        # Save meta.json in Content folder
        meta_data = {
            "post_id": new_post.id,
            "folder_name": content_folder_name,
            "topic": req.topic,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "content": card_data.model_dump(),
            "images": content_image_paths
        }
        with open(os.path.join(content_post_dir, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta_data, f, ensure_ascii=False, indent=2)

        # Update DB with image paths
        new_post.image_paths = ",".join(image_paths)
        new_post.status = PostStatus.PENDING_APPROVAL
        db.commit()
        
        return {
            "status": "success", 
            "post_id": new_post.id, 
            "folder_name": content_folder_name,
            "content": card_data.model_dump(),
            "images": content_image_paths
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        err_msg = f"{type(e).__name__}: {str(e)}" if str(e) else repr(e)
        raise HTTPException(status_code=500, detail=err_msg)

@app.get("/api/history")
def list_content_history():
    """List all saved card news history from Content/ directory."""
    history_items = []
    if not os.path.exists(CONTENT_DIR):
        return {"history": []}

    for item in os.listdir(CONTENT_DIR):
        item_path = os.path.join(CONTENT_DIR, item)
        if os.path.isdir(item_path):
            meta_file = os.path.join(item_path, "meta.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        history_items.append(meta)
                except Exception as e:
                    print(f"Error reading {meta_file}: {e}")

    # Sort history by created_at descending
    history_items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"history": history_items}

@app.get("/api/history/{folder_name}/download_zip")
def download_history_zip(folder_name: str):
    """Download ZIP archive of a historical post from Content/ folder."""
    target_dir = os.path.join(CONTENT_DIR, folder_name)
    if not os.path.exists(target_dir):
        raise HTTPException(status_code=404, detail="Content folder not found")

    import zipfile
    import io
    
    zip_filename = f"{folder_name}.zip"
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in os.listdir(target_dir):
            if file.endswith(".png") or file.endswith(".jpg"):
                full_path = os.path.join(target_dir, file)
                zip_file.write(full_path, arcname=file)
                
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={zip_filename}"
        }
    )

@app.get("/api/posts/{post_id}/download_zip")
def download_post_images_zip(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post or not post.image_paths:
        raise HTTPException(status_code=404, detail="Post or images not found")
        
    image_paths = post.image_paths.split(",")
    
    import zipfile
    import io
    
    zip_filename = f"card_news_post_{post_id}.zip"
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for img_path in image_paths:
            clean_path = img_path.strip()
            if os.path.exists(clean_path):
                filename = os.path.basename(clean_path)
                zip_file.write(clean_path, arcname=filename)
                
    zip_buffer.seek(0)
    
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={zip_filename}"
        }
    )

@app.post("/api/content/generate")
def generate_content(req: GenerateAndRenderRequest, db: Session = Depends(get_db)):
    card_data = generate_content_from_topic(req.topic)
    return {"status": "success", "data": card_data}

if __name__ == "__main__":
    import uvicorn
    print("🚀 InstaPostingPRJ Web Server is Running!")
    print("👉 Please open http://localhost:8000 or http://127.0.0.1:8000 in your browser.")
    uvicorn.run(app, host="127.0.0.1", port=8000)
