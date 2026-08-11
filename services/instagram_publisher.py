import httpx
import os

INSTAGRAM_BUSINESS_ACCOUNT_ID = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GRAPH_API_VERSION = "v19.0"
BASE_URL = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

async def create_carousel_item(image_url: str):
    url = f"{BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    payload = {
        "image_url": image_url,
        "is_carousel_item": "true",
        "access_token": ACCESS_TOKEN
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json().get("id")

async def create_carousel_container(children_ids: list, caption: str):
    url = f"{BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media"
    payload = {
        "media_type": "CAROUSEL",
        "children": ",".join(children_ids),
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json().get("id")

async def publish_container(creation_id: str):
    url = f"{BASE_URL}/{INSTAGRAM_BUSINESS_ACCOUNT_ID}/media_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=payload)
        response.raise_for_status()
        return response.json().get("id")

async def publish_carousel(image_urls: list, caption: str):
    """
    1. Create item containers for each image
    2. Create a carousel container
    3. Publish the carousel
    """
    children_ids = []
    for img_url in image_urls:
        item_id = await create_carousel_item(img_url)
        children_ids.append(item_id)
        
    carousel_id = await create_carousel_container(children_ids, caption)
    post_id = await publish_container(carousel_id)
    return post_id
