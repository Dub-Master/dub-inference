import os

import boto3
from botocore.client import ClientError
from dotenv import load_dotenv
from pyannote.audio import Pipeline
from temporalio import activity
from util import save_s3_to_file

load_dotenv()
# todo: run fully locally w/o HF (https://github.com/pyannote/pyannote-audio/issues/910)


pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization", use_auth_token=os.getenv("HUGGINGFACE_ACCESS_TOKEN")
)


@activity.defn
async def download_audio_from_s3(s3_path: str) -> str:
    print(s3_path)
    local_full_path = os.path.join("working_dir", s3_path)
    local_dir = os.path.dirname(local_full_path)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    save_s3_to_file(s3_path, local_full_path)

    return local_full_path


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
