from datetime import timedelta

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import diarize_audio


@workflow.defn
class DiarizationWorkflow:
    @workflow.run
    async def handle_media(self, audio_url: str) -> str:
        return await workflow.execute_activity(
            diarize_audio, audio_url, start_to_close_timeout=timedelta(minutes=5)
        )
