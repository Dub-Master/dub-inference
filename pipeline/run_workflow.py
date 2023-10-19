import asyncio

from temporalio.client import Client

from run_worker import SayHello


async def main():
    # Create client connected to server at the given address
    client = await Client.connect("localhost:7233")

    # Execute a workflow
    result = await client.execute_workflow(
        SayHello.run, "Temporal", id="hello-workflow", task_queue="hello-task-queue"
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
