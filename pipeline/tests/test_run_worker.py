import uuid

import pytest
from temporalio import activity
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from activities import say_hello
from workflows import SayHello


@pytest.mark.asyncio
async def test_execute_workflow():
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:

        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[SayHello],
            activities=[say_hello],
        ):
            assert "Hello, World!" == await env.client.execute_workflow(
                SayHello.run,
                "World",
                id=str(uuid.uuid4()),
                task_queue=task_queue_name,
            )


@activity.defn(name="say_hello")
async def say_hello_mocked(name: str) -> str:
    return f"Hello, {name} from mocked activity!"


@pytest.mark.asyncio
async def test_mock_activity():
    task_queue_name = str(uuid.uuid4())
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=task_queue_name,
            workflows=[SayHello],
            activities=[say_hello_mocked],
        ):
            assert "Hello, World from mocked activity!" == await env.client.execute_workflow(
                SayHello.run,
                "World",
                id=str(uuid.uuid4()),
                task_queue=task_queue_name,
            )
