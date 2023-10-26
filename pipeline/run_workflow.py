
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

    input = params.EncodingParams(
        url="https://www.youtube.com/watch?v=8ygoE2YiHCs")
    # @todo remove this hardcoding

    # Execute a workflow
    source_data = await client.execute_workflow(
        "EncodingWorkflow",
        input,
        id="encoding-workflow",
        task_queue="encoding-task-queue",
    )

    s3_url_video_file = source_data[0]
    s3_url_audio_file = source_data[1]

    diarization = await client.execute_workflow(
        "DiarizationWorkflow",
        s3_url_audio_file,
        id="diarization-workflow",
        task_queue="diarization-task-queue",
    )
    print(f"Result: {diarization}")

    core_inputs = params.CoreParams(
        s3_url_audio_file=s3_url_audio_file,
        s3_url_video_file=s3_url_video_file,
        diarization=diarization)

    output = await client.execute_workflow(
        "CoreWorkflow",
        core_inputs,
        id="core-workflow",
        task_queue="core-task-queue",
    )

    print(f"Result: {output}")


if __name__ == "__main__":
    asyncio.run(main())
