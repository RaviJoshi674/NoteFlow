import os
import json
import time
import redis

from database import (
    update_job_status,
    increment_retry,
)
from pipeline import run_pipeline


redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    decode_responses=True,
)

QUEUE_NAME = "lecture_jobs"

print("Worker started. Waiting for jobs...")

while True:
    _, data = redis_client.brpop(QUEUE_NAME)
    job = json.loads(data)

    job_id = job["jobId"]
    lecture_id = job["lectureId"]

    try:
        update_job_status(job_id, "PROCESSING")

        from database import get_lecture_file_path

        audio_path = get_lecture_file_path(lecture_id)

        # Ensure absolute path inside container
        if not audio_path.startswith("/"):
            audio_path = f"/{audio_path}"



        run_pipeline(job_id, audio_path)

        update_job_status(job_id, "COMPLETED")

    except Exception as e:
        retry_count, max_retries = increment_retry(job_id)

        if retry_count <= max_retries:
            redis_client.lpush(QUEUE_NAME, data)
        else:
            update_job_status(job_id, "FAILED", str(e))

    time.sleep(1)
