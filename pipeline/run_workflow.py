import asyncio

from common.constants import TEMPORAL_URL
from temporalio.client import Client

# from workers.encoding.workflows import EncodingWorkflow


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_URL)

    # Execute a workflow
    result = await client.execute_workflow(
        "EncodingWorkflow",
        "Temporal",
        id="encoding-workflow",
        task_queue="encoding-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
