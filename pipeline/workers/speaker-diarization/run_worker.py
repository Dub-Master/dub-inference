import asyncio
import os

from activities import diarize_audio, download_audio_from_s3
from common.constants import TEMPORAL_URL
from dotenv import load_dotenv
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import DiarizationWorkflow

load_dotenv()


async def main():
    client = await Client.connect(os.getenv("TEMPORAL_URL"), namespace="default")
    # Run the worker
    worker = Worker(
        client,
        task_queue="diarization-task-queue",
        workflows=[DiarizationWorkflow],
        activities=[diarize_audio, download_audio_from_s3],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
