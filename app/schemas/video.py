import bleach
from bson import ObjectId
from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl, validator


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        # This replaces __modify_schema__ in Pydantic v2
        return {"type": "string"}


class VideoRequest(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    url: HttpUrl

    @validator("url")
    def sanitize_url(cls, v):
        return bleach.clean(str(v))
