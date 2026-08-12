from pydantic import BaseModel, Field
from typing import List, Optional

class CardNewsFeedback(BaseModel):
    post_id: str = Field(..., description="Target card news post ID")
    score_headline: int = Field(5, ge=1, le=5, description="Headline Hook (1-5)")
    score_story: int = Field(5, ge=1, le=5, description="Story Flow (1-5)")
    score_image: int = Field(5, ge=1, le=5, description="Visual Match (1-5)")
    score_curiosity: int = Field(5, ge=1, le=5, description="Swipe Tension (1-5)")
    score_shareability: int = Field(5, ge=1, le=5, description="Shareability & Engagement (1-5)")
    quick_tags: List[str] = Field(default_factory=list, description="Selected quick feedback tags")
    user_memo: Optional[str] = Field("", description="Optional custom feedback memo")
    category: Optional[str] = Field("", description="Post category")
    emotion: Optional[str] = Field("", description="Post emotion keyword")
    created_at: Optional[str] = Field(None, description="Feedback timestamp")

    @property
    def overall_score(self) -> float:
        scores = [self.score_headline, self.score_story, self.score_image, self.score_curiosity, self.score_shareability]
        return round(sum(scores) / len(scores), 2)
