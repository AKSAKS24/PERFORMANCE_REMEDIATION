import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional
from app.schemas import RemediationRequest, RemediationResponse

@dataclass
class JobRecord:
    job_id: str
    status: str = "queued"
    request: RemediationRequest = field(default=None)
    response: Optional[RemediationResponse] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, JobRecord] = {}
        self._lock = asyncio.Lock()

    async def create(self, req: RemediationRequest) -> JobRecord:
        async with self._lock:
            job_id = uuid.uuid4().hex
            rec = JobRecord(job_id=job_id, request=req)
            self._jobs[job_id] = rec
            return rec

    async def set_status(self, job_id: str, status: str, error: Optional[str] = None) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec.status = status
                rec.error = error
                rec.updated_at = time.time()

    async def set_result(self, job_id: str, resp: RemediationResponse) -> None:
        async with self._lock:
            rec = self._jobs.get(job_id)
            if rec:
                rec.response = resp
                rec.status = "done"
                rec.updated_at = time.time()

    async def get(self, job_id: str) -> Optional[JobRecord]:
        async with self._lock:
            return self._jobs.get(job_id)

STORE = JobStore()