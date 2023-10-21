import asyncio
import os

from dotenv import load_dotenv
from temporalio.client import Client
from workers.common import params

load_dotenv()


async def main():
    # Create client connected to server at the given address
    client = await Client.connect(os.getenv("TEMPORAL_URL"))

    input = params.EncodingParams(
        url="https://www.youtube.com/watch?v=hiSfK5QrlMo")
    # @todo remove this hardcoding

    # Execute a workflow
    source_data = await client.execute_workflow(
        "EncodingWorkflow",
        input,
        id="encoding-workflow",
        task_queue="encoding-task-queue",
    )

    # source_data = [
    #     "s3://dev-input-data-bucket/8ygoE2YiHCs.mp4",
    #     "s3://dev-input-data-bucket/8ygoE2YiHCs.wav"
    # ]

    s3_url_video_file = source_data[0]
    s3_url_audio_file = source_data[1]

    # diarization = await client.execute_workflow(
    #     "DiarizationWorkflow",
    #     s3_url_audio_file,
    #     id="diarization-workflow",
    #     task_queue="diarization-task-queue",
    # )
    diarization = [{'speaker': 'SPEAKER_00', 'start': 0.8521875, 'stop': 2.4553125},
                   {'speaker': 'SPEAKER_00', 'start': 3.2990625, 'stop': 6.9103125},
                   {'speaker': 'SPEAKER_00', 'start': 7.8046875,
                       'stop': 9.002812500000001},
                   {'speaker': 'SPEAKER_00',
                       'start': 9.829687500000002, 'stop': 14.7571875},
                   {'speaker': 'SPEAKER_00', 'start': 20.8153125, 'stop': 27.2953125},
                   {'speaker': 'SPEAKER_00', 'start': 27.8859375,
                       'stop': 32.205937500000005},
                   {'speaker': 'SPEAKER_00', 'start': 32.91468750000001,
                       'stop': 43.680937500000006},
                   {'speaker': 'SPEAKER_00', 'start': 44.7946875,
                       'stop': 53.45156250000001},
                   {'speaker': 'SPEAKER_00', 'start': 54.143437500000005,
                       'stop': 57.619687500000005},
                   {'speaker': 'SPEAKER_00', 'start': 58.51406250000001,
                       'stop': 60.72468750000001},
                   {'speaker': 'SPEAKER_00', 'start': 61.38281250000001,
                       'stop': 63.49218750000001},
                   {'speaker': 'SPEAKER_00',
                       'start': 64.40343750000001, 'stop': 68.2678125},
                   {'speaker': 'SPEAKER_00', 'start': 69.0271875, 'stop': 71.1871875},
                   {'speaker': 'SPEAKER_00', 'start': 71.9296875, 'stop': 73.8534375},
                   {'speaker': 'SPEAKER_00', 'start': 74.8153125, 'stop': 77.6840625},
                   {'speaker': 'SPEAKER_00', 'start': 78.4265625, 'stop': 80.0803125},
                   {'speaker': 'SPEAKER_00', 'start': 80.9409375, 'stop': 83.5903125},
                   {'speaker': 'SPEAKER_00', 'start': 84.2146875, 'stop': 87.0159375},
                   {'speaker': 'SPEAKER_00', 'start': 87.7078125, 'stop': 91.2346875},
                   {'speaker': 'SPEAKER_00', 'start': 92.0953125, 'stop': 96.0440625},
                   {'speaker': 'SPEAKER_00', 'start': 96.9721875, 'stop': 100.9715625},
                   {'speaker': 'SPEAKER_00', 'start': 101.7984375, 'stop': 103.7390625}]
    # print(f"Result: {diarization}")

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
