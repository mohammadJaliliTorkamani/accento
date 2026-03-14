import tempfile

import yt_dlp

from app.core.logger import logger


def get_video_info(url: str):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "description": info.get("description"),
            "is_live": info.get("is_live"),
            "live_status": info.get("live_status")
        }


def download_audio(url: str, seconds: int = 15):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:

        output = f.name

        opts = {
            "format": "bestaudio/best",
            "outtmpl": output + ".%(ext)s",
            "postprocessor_args": [
                "-ss", "0",
                "-t", str(seconds)
            ],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav"
            }],
            "noplaylist": True,
            "quiet": True
        }

        try:

            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            return output + ".wav"

        except Exception:

            logger.exception("Audio download failed")

            raise
