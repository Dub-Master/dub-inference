import asyncio
import os

from activities import download_video, upload_file_to_s3
from common.constants import TEMPORAL_URL
from dotenv import load_dotenv
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from translate_activity import translate
from voice_clone_activity import text_to_speech
from workflows import EncodingWorkflow, TextToSpeechWorkflow, TranslateWorkflow

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
    translate_worker = Worker(
        client,
        task_queue="translate-task-queue",
        workflows=[TranslateWorkflow],
        activities=[translate],
    )
    text_to_speech_worker = Worker(
        client,
        task_queue="text-to-speech-task-queue",
        workflows=[TextToSpeechWorkflow],
        activities=[text_to_speech],
    )
    futures = [
        worker.run(),
        translate_worker.run(),
        text_to_speech_worker.run()
    ]
    await asyncio.gather(*futures)


if __name__ == "__main__":
    asyncio.run(main())
