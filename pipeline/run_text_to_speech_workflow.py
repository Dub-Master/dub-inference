import asyncio
import os

from temporalio.client import Client
from workers.encoding.params import TextToSpeechParams


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(os.getenv("TEMPORAL_URL"))

    # Execute a workflow
    result = await client.execute_workflow(
        "TextToSpeechWorkflow",
        TextToSpeechParams("Hello World!", "Bella"),
        id="text-to-speech-workflow",
        task_queue="text-to-speech-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
