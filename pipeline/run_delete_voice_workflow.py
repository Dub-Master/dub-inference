import asyncio
import os

from temporalio.client import Client
from workers.common.params import DeleteVoiceParams


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(os.getenv("TEMPORAL_URL"))

    # Execute a workflow
    result = await client.execute_workflow(
        "DeleteVoiceWorkflow",
        DeleteVoiceParams("d7wOdbO91b7vBTIlkTP8"),
        id="delete-voice-workflow",
        task_queue="delete-voice-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
