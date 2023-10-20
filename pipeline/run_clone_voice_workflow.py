import asyncio

from temporalio.client import Client
from workers.encoding.params import CloneVoiceParams


async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    s3_files = [
        "test_voice_clone/part1.mp3"
    ]

    # Execute a workflow
    result = await client.execute_workflow(
        "CloneVoiceWorkflow",
        CloneVoiceParams("Joe Biden", s3_files),
        id="clone-voice-workflow",
        task_queue="clone-voice-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
