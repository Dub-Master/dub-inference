import asyncio
import os

from activities import download_video
from dotenv import load_dotenv
from media_activity import (
    create_audio_segments,
    download_audio_from_s3,
    upload_file_to_s3,
)
from stitch_activity import stitch_audio

# from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from transcribe_activity import transcribe
from translate_activity import translate
from voice_clone_activity import clone_voice, delete_voice, text_to_speech
from workflows import CoreWorkflow, EncodingWorkflow

load_dotenv()


async def main():
    client = await Client.connect(os.getenv("TEMPORAL_URL"), namespace="default")
    # Run the worker
    worker = Worker(
        client,
        task_queue="encoding-task-queue",
        workflows=[EncodingWorkflow],
        activities=[download_video, upload_file_to_s3],
    )
    core_worker = Worker(
        client,
        task_queue="core-task-queue",
        workflows=[CoreWorkflow],
        activities=[translate, text_to_speech, delete_voice, stitch_audio,
                    transcribe, download_audio_from_s3, create_audio_segments,
                    upload_file_to_s3, clone_voice],
    )
    # stitch_audio_worker = Worker(
    #     client,
    #     task_queue="stitch-audio-task-queue",
    #     workflows=[StitchAudioWorkflow],
    #     activities=[stitch_audio],
    # )

    # clone_voice_worker = Worker(
    #     client,
    #     task_queue="clone-voice-task-queue",
    #     workflows=[CloneVoiceWorkflow],
    #     activities=[clone_voice],
    # )
    # delete_voice_worker = Worker(
    #     client,
    #     task_queue="delete-voice-task-queue",
    #     workflows=[DeleteVoiceWorkflow],
    #     activities=[delete_voice],
    # )

    futures = [
        worker.run(),
        core_worker.run(),
        # stitch_audio_worker.run(),

    ]
    await asyncio.gather(*futures)


if __name__ == "__main__":
    asyncio.run(main())
