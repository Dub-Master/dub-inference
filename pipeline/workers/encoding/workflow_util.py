from temporalio import workflow

def get_workflow_job_id() -> str:
    workflow_id = workflow.info().workflow_id
    job_id = workflow_id.split('-')[1]
    return job_id
