import os
import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        database=os.getenv("POSTGRES_DB"),
    )


def update_job_status(job_id, status, error_message=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE processing_jobs
        SET status = %s,
            error_message = %s
        WHERE id = %s
        """,
        (status, error_message, job_id),
    )
    conn.commit()
    conn.close()


def update_job_stage(job_id, stage):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE processing_jobs
        SET current_stage = %s
        WHERE id = %s
        """,
        (stage, job_id),
    )
    conn.commit()
    conn.close()


def increment_retry(job_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE processing_jobs
        SET retry_count = retry_count + 1
        WHERE id = %s
        RETURNING retry_count, max_retries
        """,
        (job_id,),
    )
    retry_count, max_retries = cur.fetchone()
    conn.commit()
    conn.close()
    return retry_count, max_retries

def get_lecture_file_path(lecture_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT file_path
        FROM lectures
        WHERE id = %s
        """,
        (lecture_id,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        raise ValueError("Lecture not found")

    return row[0]

