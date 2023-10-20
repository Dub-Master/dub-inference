import asyncio
import os

from dotenv import load_dotenv
from temporalio.client import Client
from workers.common.params import AudioSegment, StitchAudioParams


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(os.getenv("TEMPORAL_URL"))

    video_track = "test-stitch-audio/clip.mp4"
    audio_segments = [
        AudioSegment(0, 75, "test-stitch-audio/part1-tr.mp3"),
        AudioSegment(75, 164, "test-stitch-audio/part2-tr.mp3"),
    ]

    # Execute a workflow
    result = await client.execute_workflow(
        "StitchAudioWorkflow",
        StitchAudioParams(audio_segments, video_track),
        id="stitch-audio-workflow",
        task_queue="stitch-audio-task-queue",
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
