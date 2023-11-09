import os
from typing import Tuple

import ffmpeg
from common.params import EncodingParams, RawInputParams
from dotenv import load_dotenv
from temporalio import activity
from yt_dlp import YoutubeDL

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")

SHORTEN_VIDEO_MINUTES = os.getenv("SHORTEN_VIDEO_MINUTES", '')

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
async def download_video(params: EncodingParams) -> str:
    urls = [params.url]
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls)
    info = ydl.extract_info(params.url, download=False)
    info_json = ydl.sanitize_info(info)
    video_id = info_json["id"]

    return video_id


@activity.defn
async def shrink_inputs(params: RawInputParams) -> Tuple:
    input_file = f"{params.video_id}.mp4"
    probe = ffmpeg.probe(input_file)
    video_duration = float(probe['format']['duration'])

    if (SHORTEN_VIDEO_MINUTES != '' and
            video_duration > int(SHORTEN_VIDEO_MINUTES)*60):
        try:
            int_check = int(SHORTEN_VIDEO_MINUTES)
        except ValueError:
            raise ValueError(
                "env var 'SHORTEN_VIDEO_MINUTES' must be an integer." +
                f"It is currently set to {int_check}")

        if int(SHORTEN_VIDEO_MINUTES) <= 0:
            raise ValueError(
                "env var 'SHORTEN_VIDEO_MINUTES' must be above 0.")

        output_file = f"{params.video_id}_short.mp4"

        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(
            stream,
            output_file,
            t=int(SHORTEN_VIDEO_MINUTES)*60,
            overwrite_output=True)
        ffmpeg.run(stream)

        input_file = f"{params.video_id}.wav"
        output_file = f"{params.video_id}_short.wav"

        stream = ffmpeg.input(input_file)
        stream = ffmpeg.output(
            stream,
            output_file,
            t=int(SHORTEN_VIDEO_MINUTES)*60,
            overwrite_output=True)
        ffmpeg.run(stream)

        return (f"{params.video_id}_short.mp4",
                f"{params.video_id}_short.wav")
    else:
        return (f"{params.video_id}.mp4",
                f"{params.video_id}.wav")
