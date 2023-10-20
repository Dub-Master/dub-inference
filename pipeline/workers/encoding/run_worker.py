from dotenv import load_dotenv
load_dotenv()

import asyncio

from activities import download_video
from translate_activity import translate
from voice_clone_activity import text_to_speech
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import EncodingWorkflow, TranslateWorkflow, TextToSpeechWorkflow


async def main():
    client = await Client.connect("localhost:7233", namespace="default")
    # Run the worker
    worker = Worker(
        client,
        task_queue="encoding-task-queue",
        workflows=[EncodingWorkflow],
        activities=[download_video],
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
