from datetime import timedelta

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import download_video
    from params import TextToSpeechParams, TranslateParams
    from translate_activity import translate
    from voice_clone_activity import text_to_speech

    # from activities import download_video, upload_file_to_s3


@workflow.defn
class EncodingWorkflow:
    @workflow.run
    async def handle_media(self, url: str) -> str:
        local_video_file_path, local_audio_file_path = await workflow.execute_activity(
            download_video, url, start_to_close_timeout=timedelta(minutes=5)
        )
        return local_video_file_path, local_audio_file_path
        # s3_video_url = await workflow.execute_activity(
        #     upload_file_to_s3,
        #     local_video_file_path,
        #     s3_bucket,
        #     s3_key,
        #     start_to_close_timeout=timedelta(minutes=1),
        # )
        # s3_audio_url = await workflow.execute_activity(
        #     upload_file_to_s3,
        #     local_audio_file_path,
        #     s3_bucket,
        #     s3_key,
        #     start_to_close_timeout=timedelta(minutes=1),
        # )
        # return s3_video_url, s3_audio_url


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
