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


def download_audio(url: str, max_seconds: int = 15) -> str:
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        output_path = f.name

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": output_path + ".%(ext)s",

            "postprocessor_args": [
                "-ss", "0",
                "-t", str(max_seconds)
            ],

            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
            }],

            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                logger.info("Audio downloaded!")
                return output_path + ".wav"

        except Exception as e:
            logger.exception("Failed to download audio")

    raise Exception("Something failed while downloading the audio")
