import os

import openai
from dotenv import load_dotenv
from temporalio import activity

load_dotenv()


openai.organization = os.getenv("OPENAI_ORG_ID")
openai.api_key = os.getenv("OPENAI_API_KEY")


@activity.defn
async def transcribe(localfilepath) -> str:
    # By default, the Whisper API only supports files that are less than 25 MB
    # One way to handle this is to use the PyDub
    # open source Python package to split the audio
    audio_file = open(localfilepath, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript
