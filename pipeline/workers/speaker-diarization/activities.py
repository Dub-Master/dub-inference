import os

import boto3
from botocore.client import ClientError

# todo: run fully locally w/o HF (https://github.com/pyannote/pyannote-audio/issues/910)
from pyannote.audio import Pipeline
from temporalio import activity

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization", use_auth_token=os.getenv("HUGGINGFACE_ACCESS_TOKEN")
)


@activity.defn
async def download_audio_from_s3(s3_url: str) -> str:
    # download from s3
    s3_client = boto3.client(
        "s3",
        endpoint_url=AWS_S3_ENDPOINT_URL,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    # @todo update client initiation to use dot env

    # split s3 url into bucket and object name
    bucket_name = s3_url.split("/")[2]
    object_name = "/".join(s3_url.split("/")[3:])
    local_file_path = object_name.split("/")[-1]

    with open(local_file_path, 'wb') as f:
        s3_client.download_fileobj(bucket_name, object_name, f)

    print(local_file_path)

    return local_file_path


@activity.defn
async def diarize_audio(audio_filepath: str) -> list:
    print(audio_filepath)
    diarization_output = []

    # apply pretrained pipeline
    diarization = pipeline(audio_filepath)

    # print the result
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
        diarization_output.append(
            {
                "start": turn.start,
                "stop": turn.end,
                "speaker": speaker,
            }
        )

    # os.remove(audio_filepath)
    return diarization_output
