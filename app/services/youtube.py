import yt_dlp

def get_video_info(url: str):
    with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title"),
            "description": info.get("description")
        }

def download_audio(url: str, output_path: str):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,  # no extension here
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }],
        "quiet": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])