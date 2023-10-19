import json

from temporalio import activity
from yt_dlp import YoutubeDL

# download video using yt-dlp lib
# extract audio from video
# convert to mp4 format
# save to s3
# return url of video

ydl_opts = {
    "format": "mp4/bestvideo*+m4a/bestaudio/best",
    "keepvideo": True,
    # "remux-video": "mp4",
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    "postprocessors": [
        {  # Extract audio using ffmpeg
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }
    ],
}


@activity.defn
async def download_video(url: str) -> str:
    url = "https://www.youtube.com/watch?v=8ygoE2YiHCs"
    urls = [url]
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
    # info = ydl.extract_info(url, download=False)
    # print(json.dumps(ydl.sanitize_info(info)))
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
