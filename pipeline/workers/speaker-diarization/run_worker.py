import asyncio

from activities import diarize_audio
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import DiarizationWorkflow

from ....pipeline.common.constants import TEMPORAL_URL


async def main():
    client = await Client.connect(TEMPORAL_URL, namespace="default")
    # Run the worker
    worker = Worker(
        client,
        task_queue="speaker-diarization-task-queue",
        workflows=[DiarizationWorkflow],
        activities=[diarize_audio],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
