from datetime import datetime
from typing import Dict

from pydantic import Field, HttpUrl

from app.models.base import MongoModel


class VideoResult(MongoModel):

    url: HttpUrl

    accent: str

    confidence: float

    distribution: Dict[str, float]

    created_at: datetime = Field(default_factory=datetime.utcnow)