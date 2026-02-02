import requests
import time
import sys
import os

API_URL = "http://127.0.0.1:4000"


def upload_file(file_path):
    print(f"Uploading {file_path}...")
    with open(file_path, "rb") as f:
        files = {
            "file": f  # ✅ must match upload.single("file")
        }
        data = {
            "title": "Test Lecture"  # ✅ required by API
        }
        response = requests.post(
            f"{API_URL}/upload",
            files=files,
            data=data
        )

    if response.status_code != 201:
        print(f"Upload failed: {response.text}")
        sys.exit(1)

    return response.json()


def poll_status(job_id):
    print(f"Polling status for job {job_id}...")
    while True:
        response = requests.get(f"{API_URL}/jobs/{job_id}")

        if response.status_code != 200:
            print(f"Error checking status: {response.text}")
            return False

        data = response.json()
        status = data["status"]
        stage = data["current_stage"]

        print(f"Status: {status} | Stage: {stage}")

        if status == "COMPLETED":
            return True
        elif status == "FAILED":
            print(f"Job failed: {data.get('error_message')}")
            return False

        time.sleep(2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("No file provided. Using generated test audio...")
        file_path = "test_audio_valid.wav"
    else:
        file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

    result = upload_file(file_path)

    lecture_id = result["lectureId"]
    job_id = result["jobId"]

    print(f"Lecture ID: {lecture_id}")
    print(f"Job ID: {job_id}")

    poll_status(job_id)
