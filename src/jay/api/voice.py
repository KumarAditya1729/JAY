from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from jay.voice.tts import speak

router = APIRouter(prefix="/voice", tags=["voice"])


class SpeakRequest(BaseModel):
    text: str


@router.post("/speak")
async def speak_text(request: SpeakRequest, background_tasks: BackgroundTasks):
    """
    Speak text using the Jarvis voice asynchronously.
    """
    background_tasks.add_task(speak, request.text)
    return {"status": "ok", "message": "Speaking..."}


@router.post("/speak/sync")
async def speak_text_sync(request: SpeakRequest):
    """
    Speak text using the Jarvis voice and block until finished.
    """
    await speak(request.text)
    return {"status": "ok", "message": "Finished speaking."}
