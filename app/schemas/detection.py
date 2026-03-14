from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class VideoRequest(BaseModel):
    url: HttpUrl


class BatchRequest(BaseModel):
    urls: List[HttpUrl]


class AccentFilter(BaseModel):
    allowed_accents: Optional[List[str]] = None
    blocked_accents: Optional[List[str]] = None
