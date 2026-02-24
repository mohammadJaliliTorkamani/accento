from celery import Celery
from app.core.config import settings
from app.services.youtube import get_video_info, download_audio
from app.services.detection import contains_indian_text, detect_indian_accent
from app.core.database import collection
from app.core.cache import redis_client

celery = Celery("tasks", broker=settings.REDIS_URL)

@celery.task
def process_video(url: str):

    info = get_video_info(url)

    if contains_indian_text(info["title"]) or contains_indian_text(info["description"]):
        result = {"is_indian": True, "confidence": 1.0}
    else:
        audio_path = "/tmp/audio.wav"
        download_audio(url, audio_path)

        confidence = detect_indian_accent(audio_path)
        result = {
            "is_indian": confidence > 0.6,
            "confidence": float(confidence)
        }

    collection.insert_one({"url": url, **result})
    redis_client.set(url, str(result))

    return result