from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import json
from rq import Queue
from redis import Redis
from .worker import process_batch, init_job, get_job_key

router = APIRouter()

# Initialize Redis connection
redis_conn = Redis(host='redis', port=6379, db=0)
default_queue = Queue('default', connection=redis_conn)
batch_queue = Queue('batch', connection=redis_conn)

def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    job_key = get_job_key(job_id)
    job_data = redis_conn.hgetall(job_key)
    
    if not job_data:
        return None
        
    return {
        "job_id": job_id,
        "status": job_data[b"status"].decode(),
        "progress": int(job_data[b"progress"]),
        "total_batches": int(job_data[b"total_batches"]),
        "completed_batches": int(job_data[b"completed_batches"]),
        "result": json.loads(job_data[b"result"]) if job_data.get(b"result") else None,
        "created_at": job_data[b"created_at"].decode(),
        "updated_at": job_data[b"updated_at"].decode()
    }

class JobRequest(BaseModel):
    total_batches: int

class JobResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    total_batches: int
    completed_batches: int
    result: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

@router.post("", response_model=JobResponse)
async def create_job_endpoint(request: JobRequest):
    job_id = str(uuid.uuid4())
    
    # Initialize job in Redis
    init_job(job_id, request.total_batches)
    
    # Enqueue each batch separately to the batch queue
    for batch_id in range(1, request.total_batches + 1):
        batch_queue.enqueue(process_batch, batch_id, job_id)
    
    # Get the job state
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=500, detail="Failed to create job")
        
    return JobResponse(**job)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(**job) 