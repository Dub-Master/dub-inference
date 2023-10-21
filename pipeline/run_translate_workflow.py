import asyncio
import os

from temporalio.client import Client
from workers.common.params import TranslateParams


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(os.getenv("TEMPORAL_URL"))

    # Execute a workflow
    result = await client.execute_workflow(
        "TranslateWorkflow",
        TranslateParams("Hello World!", "Spanish"),
        id="translate-workflow",
        task_queue="translate-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
