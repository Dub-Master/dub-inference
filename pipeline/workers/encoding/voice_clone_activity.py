import os

import boto3
import requests
from dotenv import load_dotenv
from elevenlabs import generate, set_api_key
from params import TextToSpeechParams, CloneVoiceParams, DeleteVoiceParams
from temporalio import activity
import tempfile


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

@activity.defn
async def clone_voice(params: CloneVoiceParams) -> str:
    wokflow_id = activity.info().workflow_run_id
    audio_file_paths = []
    
    for s3_audio_file in params.s3_audio_files:
        audio_data = read_s3_file(s3_audio_file)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            temp_file.write(audio_data)
            audio_file_paths.append(temp_file.name)

    voice_description = f"Voice for run id {wokflow_id}"
    voice_id = eleven_labs_add_voice(params.voice_name, voice_description, audio_file_paths)

    for audio_file_path in audio_file_paths:
        os.remove(audio_file_path)

    return voice_id

@activity.defn
async def delete_voice(params: DeleteVoiceParams) -> None:
    eleven_labs_delete_voice(params.voice_id)

def read_s3_file(key: str) -> bytes:
    resp = s3_client.get_object(Bucket=AWS_S3_BUCKET, Key=key)
    return resp['Body'].read()

# https://docs.elevenlabs.io/api-reference/voices-add
def eleven_labs_add_voice(voice_name: str, voice_description: str, audio_file_paths: list[str]) -> str:
    url = "https://api.elevenlabs.io/v1/voices/add"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }
    data = {
        'name': voice_name,
        'description': voice_description
    }
    files = [
        ('files', (f'audio{id}.mp3', open(audio_file_path, 'rb'), 'audio/mpeg'))
        for id, audio_file_path in enumerate(audio_file_paths)
    ]
    resp = requests.post(url, headers=headers, data=data, files=files)
    if resp.status_code != 200:
        raise Exception(f"Failed to add voice: {resp.status_code}")
    return resp.json()['voice_id']

def eleven_labs_delete_voice(voice_id):
    url = f"https://api.elevenlabs.io/v1/voices/{voice_id}"
    headers = {
        "Accept": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }
    response = requests.delete(url, headers=headers)
    ok = response.json()["status"] == "ok"
    if not ok:
        raise Exception(f"Failed to delete voice {voice_id}")
