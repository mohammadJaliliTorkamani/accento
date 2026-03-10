import os

from bson import json_util

os.environ["HF_HOME"] = "/tmp/huggingface"

import json
from fastapi import FastAPI

from app.core.cache import redis_client
from app.core.database import collection, db
from app.schemas.video import VideoRequest
from app.tasks.celery_worker import process_video
from fastapi.encoders import jsonable_encoder

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

    url = str(request.url)

    cached = await redis_client.get(url)

    if cached:
        print("Found in Cache!!!!!!")
        return json.loads(cached)


    db_result = await collection.find_one({"url": url})

    if db_result:

        db_result = json.loads(json_util.dumps(db_result))

        await redis_client.set(url, json.dumps(db_result), ex=3600)

        return db_result

    await collection.insert_one({
        "url": url,
        "status": "processing"
    })

    process_video.delay(url)

    return {
        "status": "processing"
    }

@app.post("/detect/batch")
async def detect_batch(data: dict):

    urls = data.get("urls", [])

    results = {}

    for url in urls:

        cached = await redis_client.get(url)

        if cached:
            results[url] = json.loads(cached)
            continue

        db_result = await collection.find_one({"url": url})

        if db_result:

            db_result = json.loads(json_util.dumps(db_result))

            await redis_client.set(url, json.dumps(db_result), ex=3600)

            results[url] = db_result

        else:

            await collection.insert_one({
                "url": url,
                "status": "processing"
            })

            process_video.delay(url)

            results[url] = {"status": "processing"}

    return {"results": results}

@app.on_event("startup")
async def startup():
    from app.core.database import create_indexes
    await create_indexes()