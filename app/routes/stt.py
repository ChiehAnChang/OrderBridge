import os
import requests
from fastapi import APIRouter, File, HTTPException, UploadFile
from app.services.classifier import INTENT_ICONS, TEMPLATES, _classify_intent

router = APIRouter(prefix="/stt", tags=["STT"])

HF_STT_URL = "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3"


@router.post("")
def speech_to_text(file: UploadFile = File(...)):
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise HTTPException(status_code=500, detail="HF_TOKEN not set")

    audio_bytes = file.file.read()

    resp = requests.post(
        HF_STT_URL,
        headers={
            "Authorization": f"Bearer {hf_token}",
            "Content-Type": file.content_type or "audio/wav",
        },
        data=audio_bytes,
    )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Whisper API error: {resp.text}")

    transcript = resp.json().get("text", "").strip()
    intent = _classify_intent(transcript)
    icon = INTENT_ICONS.get(intent, "❓")
    translated_text = TEMPLATES.get(intent, {}).get("zh", transcript)

    return {
        "transcript": transcript,
        "intent": intent,
        "icon": icon,
        "translated_text": translated_text,
    }
