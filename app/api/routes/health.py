from fastapi import APIRouter

from app.core.database import db

router = APIRouter()


@router.get("/health")
async def health():
    cols = await db.list_collection_names()

    return {
        "status": "ok",
        "collections": cols
    }
