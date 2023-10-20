import os

import ffmpeg
from common.params import CreateSegmentParams
from dotenv import load_dotenv
from temporalio import activity
from util import read_s3_file, write_s3_file

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")
AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")


@activity.defn
async def download_audio_from_s3(s3_path: str) -> str:

    local_full_path = os.path.join("working_dir", s3_path)
    local_dir = os.path.dirname(local_full_path)
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    with open(local_full_path, "wb") as f:
        f.write(read_s3_file(s3_path))

    return local_full_path

data_dir = 'working_dir'


@activity.defn
async def create_audio_segments(input: CreateSegmentParams) -> list:
    local_file_paths = []

    for i, segment_definition in enumerate(input.diarization):
        print(segment_definition)
        # speaker = segment_definition['speaker']
        start = segment_definition['start']
        stop = segment_definition['stop']

        audio_input = ffmpeg.input(input.audio_local_filepath)
        audio_cut = audio_input.audio.filter(
            'atrim', start=start, duration=stop - start)
        filename = f"{i}.wav"
        local_path = os.path.join(data_dir, filename)
        audio_output = ffmpeg.output(
            audio_cut, local_path)
        ffmpeg.run(audio_output, overwrite_output=True)
        local_file_paths.append(local_path)
    return local_file_paths


@activity.defn
async def upload_file_to_s3(file_to_upload: dict
                            ) -> str:
    filename = os.path.basename(file_to_upload['local_file_path'])
    key = os.path.join(file_to_upload['folder'], filename)
    with open(file_to_upload['local_file_path'], "rb") as data:
        write_s3_file(key, data)
    return key
