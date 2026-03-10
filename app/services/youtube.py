import yt_dlp

def get_video_info(url: str):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)

        return {
            "title": info.get("title"),
            "description": info.get("description"),
            "is_live": info.get("is_live"),
            "live_status": info.get("live_status")
        }

def download_audio(url: str, output_path: str, max_seconds: int = 15):

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

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])