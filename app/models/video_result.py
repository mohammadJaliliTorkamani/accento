from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from app.models.base import MongoModel


class VideoResult(MongoModel):
    url: HttpUrl
    is_indian: bool
    confidence: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "url": "https://youtube.com/watch?v=xyz",
                "is_indian": True,
                "confidence": 0.87
            }
        }