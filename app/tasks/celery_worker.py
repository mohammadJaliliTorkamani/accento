import json
import os

from celery import Celery
from app.core.cache_sync import redis_client_sync
from app.core.config import settings
from app.core.database import collection
from app.services.youtube import get_video_info, download_audio
from app.services.detection import (
    contains_indian_text,
    detect_indian_accent,
    detect_language
)

celery = Celery(
    "tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)


@celery.task
def process_video(url: str):
    info = get_video_info(url)

    if info["is_live"] or info["live_status"] == "is_live":
        return {
            "is_indian": False,
            "confidence": 0.0,
            "reason": "live_stream_skipped"
        }

    if contains_indian_text(info["title"]) or contains_indian_text(info["description"]):
        result = {"is_indian": True, "confidence": 1.0}
    else:
        import uuid
        audio_path = f"/tmp/{uuid.uuid4()}"
        download_audio(url, audio_path)
        print("Audio downloaded!!!!!!!!!!!!!!!!!!!!!", audio_path)

        audio_path = audio_path + ".wav"

        lang = detect_language(audio_path)

        print("Detected language:", lang)

        if lang != "en":
            result = {
                "is_indian": False,
                "confidence": 0.0,
                "reason": "non_english"
            }

        else:
            confidence = detect_indian_accent(audio_path)

            result = {
                "is_indian": confidence > settings.ACCENT_THRESHOLD,
                "confidence": confidence
            }

    doc = {
        "url": url,
        "status": "done",
        **result
    }

    collection.update_one(
        {"url": url},
        {"$set": doc}
    )

    redis_client_sync.set(url, json.dumps(doc), ex=3600)

    if audio_path:
        os.remove(audio_path)

    return result
