import json

from temporalio import activity


@activity.defn
async def diarize_audio(audio_url: str) -> str:
    return f"Hello, {audio_url}!"
