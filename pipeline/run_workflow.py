import asyncio

from dotenv import load_dotenv
from temporalio.client import Client

# from workers.encoding.workflows import EncodingWorkflow

load_dotenv()


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(os.getenv("TEMPORAL_URL"))

    # Execute a workflow
    source_data = await client.execute_workflow(
        "EncodingWorkflow",
        "https://www.youtube.com/watch?v=8ygoE2YiHCs",  # @todo remove this hardcoding
        id="encoding-workflow",
        task_queue="encoding-task-queue",
    )

    s3_url_audio_file = source_data[1]

    diarization = await client.execute_workflow(
        "DiarizationWorkflow",
        s3_url_audio_file,
        id="diarization-workflow",
        task_queue="diarization-task-queue",
    )

    print(f"Result: {diarization}")


if __name__ == "__main__":
    asyncio.run(main())
