from pydantic import BaseModel, HttpUrl, validator
import bleach

class VideoRequest(BaseModel):
    url: HttpUrl

    @validator("url")
    def sanitize_url(cls, v):
        return bleach.clean(str(v))