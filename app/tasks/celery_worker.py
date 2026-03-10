from celery import Celery
from app.core.config import settings
from app.services.youtube import get_video_info, download_audio
from app.services.detection import contains_indian_text, detect_indian_accent
from app.core.database import collection
from app.core.cache import redis_client
import json

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

    if contains_indian_text(info["title"]) or contains_indian_text(info["description"]):
        result = {"is_indian": True, "confidence": 1.0}
    else:
        import uuid
        audio_path = f"/tmp/{uuid.uuid4()}"
        download_audio(url, audio_path)

        audio_path = audio_path + ".wav"
        confidence = detect_indian_accent(audio_path)

        result = {
            "is_indian": confidence > settings.ACCENT_THRESHOLD,
            "confidence": confidence
        }

    collection.insert_one({"url": url, **result})
    redis_client.set(url, json.dumps(result))

    return result