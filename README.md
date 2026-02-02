# AI-Powered Media Ingestion & Processing Platform

A production-grade backend system for processing lecture audio, interacting with an AI pipeline, and generating educational content.

## Architecture

The system is built as a set of dockerized microservices reflecting a real-world CMS workflow:

1.  **Backend API (Node.js/Express)**: Handles audio uploads, job management, and serves data with real-time WebSocket updates.
2.  **Processing Worker (Python)**: Consumes jobs from Redis, processes audio with FFmpeg, runs Whisper AI transcription, and generates content (Summary, Notes, Quiz).
3.  **Redis**: Used for the task queue and Pub/Sub for real-time WebSocket updates.
4.  **PostgreSQL**: Relational database for storing lecture metadata, job states, and results.

## Prerequisites

- Docker & Docker Compose
- Python 3.x (for running the test client locally)

## Quick Start

### 1. Start the Services
Run the following command in the project root:
```bash
docker-compose up --build
```
This will start PostgreSQL, Redis, API, and Worker services.
- API running at: `http://localhost:3000`

### 2. Verify with Automated Test Client
We have provided a script `test_client.py` to make testing easy.

**Step A: Generate a valid test file**
Because the worker expects valid audio formats (WAV/MP3), generating a dummy text file won't work. Run this script to create a valid 1-second WAV file:
```bash
python generate_audio.py
```
*This creates `test_audio_valid.wav`.*

**Step B: Run the Test**
Run the client with the generated file:
```bash
python test_client.py test_audio_valid.wav
```

**Outcome:**
1.  The file is uploaded to the API.
2.  The script polls the JOB STATUS.
3.  You will see: `QUEUED` -> `PROCESSING` -> `COMPLETED`.
4.  The script prints the **Transcript** and **AI Generated Content**.

### 3. Manual Testing via Curl
If you prefer manual testing:
```bash
# Upload
curl -X POST -F "audio=@test_audio_valid.wav" http://127.0.0.1:3000/upload

# Check Status (replace <id>)
curl http://127.0.0.1:3000/lectures/<lecture-id>/status

# Get Results
curl http://127.0.0.1:3000/lectures/<lecture-id>/results
```

## Features Implemented

- **Media Ingestion**: Multer-based uploads handling large files.
- **Async Processing**: Redis-backed job queue for decoupling upload from processing.
- **FFmpeg Pipeline**: Audio analysis and validation.
- **Whisper AI**: Speech-to-text transcription.
- **Real-Time Updates**: Socket.IO integration for live status tracking.
- **Structured Data**: PostgreSQL schema for complex relationships (Lectures -> Jobs -> Content).
