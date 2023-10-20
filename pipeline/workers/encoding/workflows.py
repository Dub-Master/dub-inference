from datetime import timedelta
from typing import Tuple

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    # from activities import download_video, upload_file_to_s3
    from activities import download_video, upload_file_to_s3
    from params import TextToSpeechParams, TranslateParams, CloneVoiceParams, DeleteVoiceParams
    from translate_activity import translate
    from voice_clone_activity import text_to_speech, clone_voice, delete_voice


@workflow.defn
class EncodingWorkflow:
    @workflow.run
    async def handle_media(self, url: str) -> Tuple:
        (
            local_video_file_path,
            local_audio_file_path,
        ) = await workflow.execute_activity(
            download_video, url, start_to_close_timeout=timedelta(minutes=15)
        )
        s3_video_url = await workflow.execute_activity(
            upload_file_to_s3,
            local_video_file_path,
            start_to_close_timeout=timedelta(minutes=15),
        )
        s3_audio_url = await workflow.execute_activity(
            upload_file_to_s3,
            local_audio_file_path,
            start_to_close_timeout=timedelta(minutes=15),
        )
        return (s3_video_url, s3_audio_url)


@workflow.defn
class TranslateWorkflow:
    @workflow.run
    async def handle(self, params: TranslateParams) -> str:
        return await workflow.execute_activity(
            translate, params, start_to_close_timeout=timedelta(minutes=1)
        )


@workflow.defn
class TextToSpeechWorkflow:
    @workflow.run
    async def handle(self, params: TextToSpeechParams) -> str:
        return await workflow.execute_activity(
            text_to_speech, params, start_to_close_timeout=timedelta(minutes=5)
        )


@workflow.defn
class CloneVoiceWorkflow:
    @workflow.run
    async def handle(self, params: CloneVoiceParams) -> str:
        return await workflow.execute_activity(
            clone_voice, params, start_to_close_timeout=timedelta(minutes=5)
        )


@workflow.defn
class DeleteVoiceWorkflow:
    @workflow.run
    async def handle(self, params: DeleteVoiceParams) -> None:
        await workflow.execute_activity(
            delete_voice, params, start_to_close_timeout=timedelta(minutes=5)
        )
