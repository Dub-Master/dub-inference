import os

import boto3
from dotenv import load_dotenv
from elevenlabs import generate, set_api_key
from params import TextToSpeechParams
from temporalio import activity

load_dotenv()
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")

set_api_key(ELEVEN_LABS_API_KEY)

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=AWS_S3_ENDPOINT_URL
)


@activity.defn
async def text_to_speech(params: TextToSpeechParams) -> str:
    audio_data = generate(params.text, voice=params.voice)
    wokflow_id = activity.info().workflow_run_id
    s3_key = f"output-voice-{wokflow_id}.mp3"
    s3_client.put_object(Bucket=AWS_S3_BUCKET, Key=s3_key, Body=audio_data)
    return s3_key
