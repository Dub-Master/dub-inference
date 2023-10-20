from datetime import timedelta
from typing import Tuple

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import download_video
    from translate_activity import translate
    from voice_clone_activity import text_to_speech
    from params import TranslateParams, TextToSpeechParams


@workflow.defn
class EncodingWorkflow:
    @workflow.run
    async def handle_media(self, url: str) -> str:
        return await workflow.execute_activity(
            download_video, url, start_to_close_timeout=timedelta(minutes=5)
        )

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
