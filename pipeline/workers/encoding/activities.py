import json

from temporalio import activity
from yt_dlp import YoutubeDL

# download video using yt-dlp lib
# extract audio from video
# convert to mp4 format
# save to s3
# return url of video

ydl_opts = {
    "format": "m4a/bestaudio/best",
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    "postprocessors": [
        {  # Extract audio using ffmpeg
            "key": "FFmpegExtractAudio",
            "preferredcodec": "m4a",
        }
    ],
}


@activity.defn
async def download_video(url: str) -> str:
    url = "https://www.youtube.com/watch?v=8ygoE2YiHCs"
    urls = [url]
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
    info = ydl.extract_info(url, download=False)
    print(json.dumps(ydl.sanitize_info(info)))
    return f"Hello, {url}!"


# @activity.defn
# async def convert_video(url: str) -> str:
#     return f"Hello, {url}!"


# @activity.defn
# async def extract_audio(url: str) -> str:
#     return f"Hello, {url}!"


# @activity.defn
# async def save_files(url: str) -> str:
#     return f"Hello, {url}!"
