from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from models.database import SessionLocal
from models.post import Post, PostStatus
from services.instagram_publisher import publish_carousel
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_and_publish_approved_posts():
    db = SessionLocal()
    try:
        # Find approved posts that are scheduled for now or in the past, or just approved and ready
        posts = db.query(Post).filter(Post.status == PostStatus.APPROVED).all()
        for post in posts:
            logger.info(f"Publishing post {post.id}")
            # The images need to be accessible via public URLs for Instagram API
            # For this MVP, we assume image_paths are public URLs or handled via a static server
            image_urls = post.image_paths.split(",")
            
            try:
                ig_post_id = await publish_carousel(image_urls, post.caption)
                post.status = PostStatus.PUBLISHED
                logger.info(f"Post {post.id} published successfully with IG ID {ig_post_id}")
            except Exception as e:
                post.status = PostStatus.FAILED
                logger.error(f"Failed to publish post {post.id}: {e}")
            
            db.commit()
    finally:
        db.close()

def start_scheduler():
    # Run every minute to check for approved posts
    scheduler.add_job(check_and_publish_approved_posts, CronTrigger(minute="*"))
    scheduler.start()
