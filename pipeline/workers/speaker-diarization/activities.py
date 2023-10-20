import os

import boto3
from botocore.client import ClientError
from common.secret import HUGGINGFACE_ACCESS_TOKEN as HF_ACCESS_TOKEN
from common.secret import S3_ACCESS_ID, S3_ACCESS_KEY, S3_BUCKET, S3_ENDPOINT, S3_REGION

# todo: run fully locally w/o HF (https://github.com/pyannote/pyannote-audio/issues/910)
from pyannote.audio import Pipeline
from temporalio import activity

pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization", use_auth_token=HF_ACCESS_TOKEN
)


@activity.defn
async def download_audio_from_s3(s3_url: str) -> str:
    # download from s3
    s3_client = boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_ID,
        aws_secret_access_key=S3_ACCESS_KEY,
        region_name=S3_REGION,
    )
    # @todo update client initiation to use dot env

    # split s3 url into bucket and object name
    bucket_name = s3_url.split("/")[2]
    object_name = "/".join(s3_url.split("/")[3:])
    local_file_path = object_name.split("/")[-1]

    print(bucket_name)
    print(object_name)
    print(local_file_path)

    with open(local_file_path, 'wb') as f:
        s3_client.download_fileobj(bucket_name, object_name, f)

    return local_file_path


@activity.defn
async def diarize_audio(audio_filepath: str) -> dict:
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

    os.remove(audio_filepath)
    return diarization
