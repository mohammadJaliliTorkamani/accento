import json

from bson import json_util
from fastapi import APIRouter

from app.core.cache import redis_client
from app.core.database import collection
from app.schemas.detection import VideoRequest, BatchRequest
from app.workers.celery_worker import process_video_task

router = APIRouter()


@router.post("/detect")
async def detect_video(request: VideoRequest):
    url = str(request.url)

    cached = await redis_client.get(url)

    if cached:
        return json.loads(cached)

    db_result = await collection.find_one({"url": url})

    if db_result:
        return json.loads(json_util.dumps(db_result))

    await collection.insert_one({
        "url": url,
        "status": "processing"
    })

    process_video_task.delay(url)

    return {"status": "processing"}


@router.post("/detect/batch")
async def detect_batch(request: BatchRequest):
    results = {}

    for url in request.urls:
        process_video_task.delay(str(url))

        results[str(url)] = {"status": "processing"}

    return results
