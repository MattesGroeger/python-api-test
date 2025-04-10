import time
import uuid
import json
from rq import Worker, Queue, Connection
from redis import Redis
from typing import Dict, Any

# Initialize Redis connection
redis_conn = Redis(host='redis', port=6379, db=0)

# Create multiple queues for better distribution
default_queue = Queue('default', connection=redis_conn)
batch_queue = Queue('batch', connection=redis_conn)

def get_job_key(job_id: str) -> str:
    return f"job:{job_id}"

def init_job(job_id: str, total_batches: int):
    """Initialize a new job in Redis"""
    job_key = get_job_key(job_id)
    redis_conn.hmset(job_key, {
        "status": "pending",
        "progress": "0",
        "total_batches": str(total_batches),
        "completed_batches": "0",
        "created_at": str(time.time()),
        "updated_at": str(time.time())
    })
    # Set TTL to 24 hours
    redis_conn.expire(job_key, 24 * 60 * 60)

def update_job_progress(job_id: str, batch_id: int):
    """Update job progress atomically using Redis"""
    job_key = get_job_key(job_id)
    
    # Use Redis pipeline for atomic operations
    pipe = redis_conn.pipeline()
    
    # Increment completed_batches atomically
    pipe.hincrby(job_key, "completed_batches", 1)
    
    # Get the updated values
    pipe.hgetall(job_key)
    
    # Execute the pipeline and get results
    results = pipe.execute()
    
    # Get the job data from the second operation
    job_data = results[1]
    
    # Calculate and update progress
    completed = int(job_data[b"completed_batches"])
    total = int(job_data[b"total_batches"])
    progress = int((completed / total) * 100)
    
    # Update progress and timestamp
    redis_conn.hmset(job_key, {
        "progress": str(progress),
        "updated_at": str(time.time())
    })

def update_job_status(job_id: str, status: str, result: Dict[str, Any] = None):
    """Update job status in Redis"""
    job_key = get_job_key(job_id)
    
    # Prepare the update data
    update_data = {
        "status": status,
        "updated_at": str(time.time())
    }
    
    # Only add result if it's not None
    if result is not None:
        update_data["result"] = json.dumps(result)
    
    # Update the job status
    redis_conn.hmset(job_key, update_data)

def process_batch(batch_id: int, job_id: str) -> Dict[str, Any]:
    """Process a single batch of tasks"""
    try:
        # Simulate some work
        time.sleep(2)
        
        # Update job progress in database
        update_job_progress(job_id, batch_id)
        
        # Check if this was the last batch after updating progress
        job_key = get_job_key(job_id)
        job_data = redis_conn.hgetall(job_key)
        
        completed = int(job_data[b"completed_batches"])
        total = int(job_data[b"total_batches"])
        
        # Only mark as completed if we've processed all batches
        if completed == total:
            # Update status to completed and ensure progress is 100%
            redis_conn.hmset(job_key, {
                "status": "completed",
                "progress": "100",
                "updated_at": str(time.time())
            })
            # Set shorter TTL for completed jobs (1 hour)
            redis_conn.expire(job_key, 60 * 60)
        
        return {
            "batch_id": batch_id,
            "status": "completed",
            "timestamp": time.time()
        }
    except Exception as e:
        update_job_status(job_id, "failed", {"error": str(e)})
        raise

if __name__ == '__main__':
    with Connection(redis_conn):
        # Listen on both queues
        worker = Worker([default_queue, batch_queue])
        worker.work() 