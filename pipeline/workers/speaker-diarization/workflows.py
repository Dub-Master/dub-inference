from datetime import timedelta

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import diarize_audio, download_audio_from_s3


@workflow.defn
class DiarizationWorkflow:
    @workflow.run
    async def handle_media(self, s3_url: str) -> str:
        filename = await workflow.execute_activity(
            download_audio_from_s3,
            s3_url,
            start_to_close_timeout=timedelta(minutes=5))

        diarization = await workflow.execute_activity(
            diarize_audio, filename, start_to_close_timeout=timedelta(
                minutes=20)
        )
        return diarization
