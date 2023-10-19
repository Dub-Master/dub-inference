import asyncio

from activities import download_video
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from workflows import EncodingWorkflow


async def main():
    client = await Client.connect("localhost:7233", namespace="default")
    # Run the worker
    worker = Worker(
        client,
        task_queue="encoding-task-queue",
        workflows=[EncodingWorkflow],
        activities=[download_video],
    )
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
