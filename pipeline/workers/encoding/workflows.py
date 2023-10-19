from datetime import timedelta
from typing import Tuple

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import download_video


@workflow.defn
class EncodingWorkflow:
    @workflow.run
    async def handle_media(self, url: str) -> str:
        return await workflow.execute_activity(
            download_video, url, start_to_close_timeout=timedelta(minutes=5)
        )
