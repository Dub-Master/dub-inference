import asyncio
import os

from activities import download_video, shrink_inputs
from dotenv import load_dotenv
from media_activity import (
    create_audio_segments,
    download_audio_from_s3,
    upload_file_to_s3,
)
from stitch_activity import combine_audio_video, stitch_audio

from temporalio.client import Client
from temporalio.worker import Worker
from transcribe_activity import transcribe
from translate_activity import translate
from voice_clone_activity import clone_voice, delete_voice, text_to_speech
from workflows import CoreWorkflow, E2EWorkflow, EncodingWorkflow

load_dotenv()

TEMPORAL_URL = os.getenv("TEMPORAL_URL")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE") or "default"


async def main():
    client = await Client.connect(
        TEMPORAL_URL, 
        namespace=TEMPORAL_NAMESPACE
    )
    worker = Worker(
        client,
        task_queue="encoding-task-queue",
        workflows=[EncodingWorkflow],
        activities=[download_video, shrink_inputs, upload_file_to_s3],
    )
    core_worker = Worker(
        client,
        task_queue="core-task-queue",
        workflows=[CoreWorkflow],
        activities=[translate, text_to_speech,
                    delete_voice, stitch_audio, combine_audio_video,
                    transcribe, download_audio_from_s3, create_audio_segments,
                    upload_file_to_s3, clone_voice],
    )
    e2e_worker = Worker(
        client,
        task_queue="e2e-task-queue",
        workflows=[E2EWorkflow],
        activities=[],
    )

    futures = [
        worker.run(),
        core_worker.run(),
        e2e_worker.run(),
    ]
    await asyncio.gather(*futures)


if __name__ == "__main__":
    asyncio.run(main())
