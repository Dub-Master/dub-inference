import json
from typing import Tuple

import boto3
from common.secret import S3_ACCESS_ID, S3_ACCESS_KEY, S3_BUCKET, S3_REGION
from temporalio import activity
from yt_dlp import YoutubeDL

ydl_opts = {
    "format": "mp4/bestvideo*+m4a/bestaudio/best",
    "keepvideo": True,
    "outtmpl": "%(id)s.%(ext)s",
    # "writeinfojson": True,
    # ℹ️ See help(yt_dlp.postprocessor) for a list of available Postprocessors and their arguments
    "postprocessors": [
        {  # Extract audio using ffmpeg
            "key": "FFmpegExtractAudio",
            "preferredcodec": "wav",
        }
    ],
}


@activity.defn
async def download_video(url: str) -> Tuple:
    url = "https://www.youtube.com/watch?v=8ygoE2YiHCs"
    urls = [url]
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
    info = ydl.extract_info(url, download=False)
    info_json = ydl.sanitize_info(info)
    video_id = info_json["id"]
    return (f"{video_id}.mp4", f"{video_id}.wav")


@activity.defn
async def upload_file_to_s3(local_file_path: str) -> str:
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=S3_ACCESS_ID,
        aws_secret_access_key=S3_ACCESS_KEY,
        region_name=S3_REGION,
    )
    with open(local_file_path, "rb") as data:
        s3_client.upload_fileobj(data, S3_BUCKET, local_file_path)
    return "s3://" + S3_BUCKET + "/" + local_file_path
