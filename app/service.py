import asyncio
from fastapi import HTTPException
from datetime import date
from typing import Optional
from app.schemas import (
    RemediationRequest,
    RemediationResponse,
    JobIdResponse,
    JobStatusResponse,
)
from app.llm import run_chain
from app.utils import strip_markdown_fences
from app.store import STORE

async def _process_job(job_id: str) -> None:
    rec = await STORE.get(job_id)
    if not rec:
        return
    await STORE.set_status(job_id, "running")
    req = rec.request
    system_date = date.today().isoformat()
    try:
        llm_output = await run_chain(system_date, req.code)
        remediated = strip_markdown_fences(llm_output)
        if not remediated:
            await STORE.set_status(job_id, "error", error="Empty remediation returned by AI.")
            return
        resp = RemediationResponse(
            pgm_name=req.pgm_name,
            inc_name=req.inc_name,
            type=req.type,
            name=req.name or "",
            class_implementation=req.class_implementation or "",
            original_code=req.code,
            remediated_code=remediated,
        )
        await STORE.set_result(job_id, resp)
    except Exception as e:
        await STORE.set_status(job_id, "error", error=str(e))

async def enqueue_remediation(req: RemediationRequest) -> JobIdResponse:
    if not req.code or not req.code.strip():
        raise HTTPException(status_code=400, detail="Field 'code' must contain ABAP source.")
    rec = await STORE.create(req)
    asyncio.create_task(_process_job(rec.job_id))
    return JobIdResponse(job_id=rec.job_id)

async def get_job_status(job_id: str) -> Optional[JobStatusResponse]:
    rec = await STORE.get(job_id)
    if not rec:
        return None
    return JobStatusResponse(job_id=rec.job_id, status=rec.status, error=rec.error)

async def get_job_result(job_id: str) -> Optional[RemediationResponse]:
    rec = await STORE.get(job_id)
    if not rec or rec.status != "done" or not rec.response:
        return None
    return rec.response