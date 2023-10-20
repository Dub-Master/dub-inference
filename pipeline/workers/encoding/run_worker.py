import asyncio
import os

from activities import download_video, upload_file_to_s3
from dotenv import load_dotenv
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker
from translate_activity import translate
from voice_clone_activity import text_to_speech, clone_voice, delete_voice
from stitch_activity import stitch_audio
from workflows import EncodingWorkflow, TextToSpeechWorkflow, TranslateWorkflow, CloneVoiceWorkflow, DeleteVoiceWorkflow, StitchAudioWorkflow

load_dotenv()


async def main():
    client = await Client.connect(os.getenv("TEMPORAL_URL"), namespace="default")
    # Run the worker
    worker = Worker(
        client,
        task_queue="encoding-task-queue",
        workflows=[EncodingWorkflow],
        activities=[download_video, upload_file_to_s3],
    )
    translate_worker = Worker(
        client,
        task_queue="translate-task-queue",
        workflows=[TranslateWorkflow],
        activities=[translate],
    )
    text_to_speech_worker = Worker(
        client,
        task_queue="text-to-speech-task-queue",
        workflows=[TextToSpeechWorkflow],
        activities=[text_to_speech],
    )
    clone_voice_worker = Worker(
        client,
        task_queue="clone-voice-task-queue",
        workflows=[CloneVoiceWorkflow],
        activities=[clone_voice],
    )
    delete_voice_worker = Worker(
        client,
        task_queue="delete-voice-task-queue",
        workflows=[DeleteVoiceWorkflow],
        activities=[delete_voice],
    )
    stitch_audio_worker = Worker(
        client,
        task_queue="stitch-audio-task-queue",
        workflows=[StitchAudioWorkflow],
        activities=[stitch_audio],
    )

    futures = [
        worker.run(),
        translate_worker.run(),
        text_to_speech_worker.run(),
        clone_voice_worker.run(),
        delete_voice_worker.run(),
        stitch_audio_worker.run(),
    ]
    await asyncio.gather(*futures)


if __name__ == "__main__":
    asyncio.run(main())
