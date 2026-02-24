from fastapi import FastAPI, Depends

from app.core import database
from app.schemas.video import VideoRequest
from app.tasks.celery_worker import process_video
from app.core.database import collection, db
from app.core.cache import redis_client
import json

app = FastAPI()

@app.get("/health")
async def health_check():
    collections = await db.list_collection_names()
    return {
        "status": "OK",
        "collections": collections
    }

@app.post("/detect")
async def detect_video(request: VideoRequest):

    cached = redis_client.get(request.url)
    if cached:
        return json.loads(cached)

    db_result = await collection.find_one({"url": request.url})
    if db_result:
        redis_client.set(request.url, str(db_result))
        return db_result

    task = process_video.delay(request.url)

    return {"message": "Processing started", "task_id": task.id}