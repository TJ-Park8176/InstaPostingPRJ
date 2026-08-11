from pydantic import BaseModel, Field
from typing import List, Optional

class SlideBase(BaseModel):
    title: str = Field(description="The main title of the body slide")
    subtitle: Optional[str] = Field(default="", description="Subtitle or subheadline for additional context")
    story_text: str = Field(description="Rich, detailed 2-3 sentence narrative paragraph explaining the event, context, and dramatic details")
    bullet_points: List[str] = Field(default_factory=list, description="2-3 actionable, detailed bullet points explaining the core point")
    key_tip: Optional[str] = Field(default="", description="A highlighted tip, warning, or takeaway box text")
    image_prompt: str = Field(description="English image generation prompt describing the dramatic animal scene")

class CoverSlide(BaseModel):
    tagline: str = Field(description="Catchy top tagline e.g. '😱 해외 엽기 실화' or '🔥 세계 동물 사건'")
    title: str = Field(description="Main bold catchy headline for the cover")
    subtitle: str = Field(description="Sub headline providing context or hook")
    image_prompt: str = Field(description="English image generation prompt describing the cover animal scene")

class CTASlide(BaseModel):
    title: str = Field(description="Call to action headline e.g. '도움이 되셨나요?'")
    content: str = Field(description="Call to action text e.g. '좋아요 & 저장해두고 친구에게 공유해보세요!'")
    image_prompt: str = Field(description="English image generation prompt for the closing CTA scene")

class CardNewsData(BaseModel):
    category: str = Field(description="Category tag e.g. '세계동물뉴스', '엽기동물실화'")
    source_name: str = Field(description="Verified news source publisher e.g. 'BBC World', 'Daily Mail', '역사 속 실화'")
    source_url: str = Field(description="Original verified news URL link")
    is_historical_fallback: bool = Field(description="True if this is a historical story, False if real-time news")
    cover: CoverSlide = Field(description="The cover slide")
    body_slides: List[SlideBase] = Field(description="Body slides with rich structured information (4 slides for full storytelling)")
    cta: CTASlide = Field(description="The closing CTA slide")
    caption: str = Field(description="Detailed, engaging Instagram post caption with emojis and source credit")
    hashtags: List[str] = Field(description="List of 15-20 viral hashtags without # symbol")
