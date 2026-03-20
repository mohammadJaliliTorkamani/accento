import json
import os

from app.core.cache_sync import redis_client_sync
from app.core.database_sync import collection
from app.core.logger import logger
from app.services.accent_service import detect_accent
from app.services.language_service import detect_language
from app.services.youtube_service import (
    get_video_info,
    download_audio
)


def process_video(url: str):
    logger.info(f"Processing request for {url}")

    cached = redis_client_sync.get(url)

    if cached:
        logger.info(f"Redis hit for {url}")
        return json.loads(cached)

    db_result = collection.find_one({"url": url})

    if db_result and db_result.get("status") == "done":
        logger.info(f"MongoDB hit for {url}")

        redis_client_sync.set(
            url,
            json.dumps(db_result, default=str),
            ex=3600
        )

        return db_result

    info = get_video_info(url)
    audio_path = None

    try:

        if info["is_live"] or info["live_status"] == "is_live":

            result = {
                "status": "done",
                "url": url,
                "accent": None,
                "confidence": 0.0,
                "reason": "live_stream_skipped"
            }

        else:

            audio_path = download_audio(url)

            lang = detect_language(audio_path)

            logger.info(f"Detected language: {lang}")

            if lang.lower() != "en":

                result = {
                    "status": "done",
                    "url": url,
                    "accent": None,
                    "confidence": 0.0,
                    "reason": "non_english"
                }

            else:

                accent, confidence, _ = detect_accent(audio_path)

                result = {
                    "status": "done",
                    "url": url,
                    "accent": accent,
                    "confidence": confidence
                }

        # -------------------------
        # SAVE TO DATABASE
        # -------------------------

        collection.update_one(
            {"url": url},
            {"$set": result},
            upsert=True
        )

        # -------------------------
        # SAVE TO REDIS CACHE
        # -------------------------

        redis_client_sync.set(
            url,
            json.dumps(result),
            ex=3600
        )

        return result

    except Exception:
        logger.exception("Video processing failed")

        result = {
            "status": "error",
            "url": url,
            "accent": None,
            "confidence": 0.0
        }

        return result

    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
