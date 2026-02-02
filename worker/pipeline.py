import os
import whisper

from database import update_job_stage

MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
model = whisper.load_model(MODEL_NAME)


def run_pipeline(job_id: str, audio_path: str):
    """
    Audio processing pipeline:
    TRANSCRIBING -> GENERATING -> COMPLETED
    """

    update_job_stage(job_id, "TRANSCRIBING")

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    result = model.transcribe(audio_path)
    transcript = result.get("text", "").strip()
    language = result.get("language")

    if not transcript:
        raise ValueError("Generated empty transcript")

    update_job_stage(job_id, "GENERATING")

    notes = {
        "language": language,
        "summary": transcript[:600],
        "key_points": [
            sentence.strip()
            for sentence in transcript.split(".")
            if len(sentence.strip()) > 20
        ][:5],
    }

    update_job_stage(job_id, "COMPLETED")

    return transcript, notes
