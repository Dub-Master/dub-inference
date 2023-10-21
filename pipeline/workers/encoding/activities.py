import os
from typing import Tuple

from common.params import EncodingParams
from dotenv import load_dotenv
from temporalio import activity
from yt_dlp import YoutubeDL

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")

ydl_opts = {
    "format": "mp4/bestvideo*+m4a/bestaudio/best",
    "keepvideo": True,
    "outtmpl": "%(id)s.%(ext)s",
    # "writeinfojson": True,
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors
    # and their arguments
    "postprocessors": [
        {  # Extract audio as wav using ffmpeg
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }
    ],
}


@activity.defn
async def download_video(params: EncodingParams) -> Tuple:
    urls = [params.url]
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
    info = ydl.extract_info(params.url, download=False)
    info_json = ydl.sanitize_info(info)
    video_id = info_json["id"]
    return (f"{video_id}.mp4", f"{video_id}.wav")
