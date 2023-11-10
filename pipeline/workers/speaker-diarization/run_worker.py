import asyncio
import os

from activities import diarize_audio, download_audio_from_s3
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import DiarizationWorkflow

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
        task_queue="diarization-task-queue",
        workflows=[DiarizationWorkflow],
        activities=[diarize_audio, download_audio_from_s3],
        max_concurrent_activities=1
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
