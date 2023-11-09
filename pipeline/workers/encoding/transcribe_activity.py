import os

import openai
from common.params import TranscribeParams
from dotenv import load_dotenv
from ffprobe import FFProbe
from temporalio import activity

load_dotenv()


openai.organization = os.getenv("OPENAI_ORG_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")


@activity.defn
async def transcribe(params: TranscribeParams) -> str:
    # By default, the Whisper API only supports files that are less than 25 MB
    # One way to handle this is to use the PyDub
    # open source Python package to split the audio

    audio_file = params.audio_file_url
    # Use ffprobe to get the duration of the audio file
    metadata = FFProbe(audio_file)
    duration = float(metadata.streams[0].duration)
    # If the audio file is less than 0.1 seconds, return an empty string
    if duration < 0.1:
        return ""
    else:
        audio_file = open(audio_file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
        print('transcript', transcript)
        return transcript['text']
