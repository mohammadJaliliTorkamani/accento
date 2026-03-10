import os
os.environ["HF_HOME"] = "/tmp/huggingface"

import json
from fastapi import FastAPI

from app.core.cache import redis_client
from app.core.database import collection, db
from app.schemas.video import VideoRequest
from app.tasks.celery_worker import process_video

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
        try:
            return json.loads(cached.decode())
        except Exception:
            redis_client.delete(request.url)

    db_result = await collection.find_one({"url": request.url})

    if db_result:
        db_result["_id"] = str(db_result["_id"])

        redis_client.set(
            request.url,
            json.dumps(db_result),
            ex=3600
        )

        return db_result

    task = process_video.delay(request.url)

    return {
        "message": "Processing started",
        "task_id": task.id
    }