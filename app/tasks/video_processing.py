import os
import json

from app.core.database import collection
from app.core.cache_sync import redis_client_sync
from app.core.logger import logger

from app.services.youtube_service import (
    get_video_info,
    download_audio
)

from app.services.language_service import detect_language
from app.services.accent_service import detect_accent


def process_video(url: str):

    audio_path = None

    try:

        info = get_video_info(url)

        if info["is_live"]:

            result = {
                "status": "skipped",
                "reason": "live_stream"
            }

        else:

            audio_path = download_audio(url)

            lang = detect_language(audio_path)

            if lang != "en":

                result = {
                    "status": "non_english"
                }

            else:

                accent, confidence, dist = detect_accent(audio_path)

                result = {
                    "status": "done",
                    "accent": accent,
                    "confidence": confidence,
                    "distribution": dist
                }

        collection.update_one(
            {"url": url},
            {"$set": {"url": url, **result}},
            upsert=True
        )

        redis_client_sync.set(
            url,
            json.dumps(result),
            ex=3600
        )

        return result

    except Exception:

        logger.exception("processing failed")

        return {"status": "error"}

    finally:

        if audio_path and os.path.exists(audio_path):

            os.remove(audio_path)