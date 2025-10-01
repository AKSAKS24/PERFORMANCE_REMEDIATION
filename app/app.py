from fastapi import FastAPI, HTTPException
from app.schemas import RemediationRequest, JobIdResponse, JobStatusResponse, RemediationResponse
from app.service import enqueue_remediation, get_job_status, get_job_result

app = FastAPI(title="ABAP Performance Remediator (Background Jobs)")

@app.post("/remediate", response_model=JobIdResponse)
async def remediate_enqueue(req: RemediationRequest) -> JobIdResponse:
    return await enqueue_remediation(req)

@app.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def job_status(job_id: str) -> JobStatusResponse:
    status = await get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return status

@app.get("/remediate/{job_id}", response_model=RemediationResponse)
async def job_result(job_id: str) -> RemediationResponse:
    result = await get_job_result(job_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Job not found or not completed")
    return result