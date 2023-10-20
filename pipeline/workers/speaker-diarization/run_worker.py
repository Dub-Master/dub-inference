import asyncio

from activities import diarize_audio, download_audio_from_s3
from common.constants import TEMPORAL_URL
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import DiarizationWorkflow


async def main():
    client = await Client.connect(TEMPORAL_URL, namespace="default")
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
