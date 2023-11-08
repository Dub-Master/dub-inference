
import asyncio
import os

from dotenv import load_dotenv
from temporalio.client import Client
from workers.common import params

load_dotenv()

TEMPORAL_URL = os.getenv("TEMPORAL_URL")
TEMPORAL_NAMESPACE = os.getenv("TEMPORAL_NAMESPACE") or "default"


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(TEMPORAL_URL, namespace=TEMPORAL_NAMESPACE)

    input = params.E2EParams(
        url="https://www.youtube.com/watch?v=8ygoE2YiHCs")
    # @todo remove this hardcoding

    # Execute a workflow
    output = await client.execute_workflow(
        "E2EWorkflow",
        input,
        id="e2e-workflow",
        task_queue="e2e-task-queue",
    )

    print(f"Result: {output}")


if __name__ == "__main__":
    asyncio.run(main())
