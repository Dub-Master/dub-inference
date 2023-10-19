import asyncio

from temporalio.client import Client
from workflows import EncodingWorkflow


async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # Execute a workflow
    result = await client.execute_workflow(
        EncodingWorkflow.handle_media,
        "Temporal",
        id="encoding-workflow",
        task_queue="encoding-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
