import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from openai import OpenAI

ROOT = Path(__file__).resolve().parent
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = FastAPI(title="VoxTranslate AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "50"))

class TranslateRequest(BaseModel):
    text: str
    targetLanguage: str

class SpeakRequest(BaseModel):
    text: str

@app.get("/api/health")
def health():
    return {"ok": True, "service": "VoxTranslate AI"}

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if not client.api_key:
        raise HTTPException(500, "OPENAI_API_KEY is not configured on the server.")

    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty audio/video file.")
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(413, f"File is larger than {MAX_UPLOAD_MB} MB.")

    try:
        result = client.audio.transcriptions.create(
            model=os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-transcribe"),
            file=(file.filename or "audio.webm", data, file.content_type or "application/octet-stream"),
            response_format="json",
        )
        return {"text": getattr(result, "text", "")}
    except Exception as exc:
        raise HTTPException(502, f"Transcription failed: {exc}")

@app.post("/api/translate")
def translate(body: TranslateRequest):
    if not client.api_key:
        raise HTTPException(500, "OPENAI_API_KEY is not configured on the server.")
    if not body.text.strip() or not body.targetLanguage.strip():
        raise HTTPException(400, "text and targetLanguage are required.")

    prompt = (
        f"Translate the following transcript into {body.targetLanguage}. "
        "Preserve meaning, names, tone, formatting and paragraph breaks. "
        "Return only the translation.\n\n" + body.text
    )
    try:
        response = client.responses.create(
            model=os.getenv("OPENAI_TRANSLATE_MODEL", "gpt-5.6-luna"),
            input=prompt,
        )
        return {"translation": response.output_text}
    except Exception as exc:
        raise HTTPException(502, f"Translation failed: {exc}")

@app.post("/api/speak")
def speak(body: SpeakRequest):
    if not client.api_key:
        raise HTTPException(500, "OPENAI_API_KEY is not configured on the server.")
    if not body.text.strip():
        raise HTTPException(400, "text is required.")

    try:
        audio = client.audio.speech.create(
            model=os.getenv("OPENAI_TTS_MODEL", "gpt-4o-mini-tts"),
            voice=os.getenv("OPENAI_TTS_VOICE", "coral"),
            input=body.text,
            response_format="mp3",
        )
        return StreamingResponse(
            iter([audio.read()]),
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-store"},
        )
    except Exception as exc:
        raise HTTPException(502, f"Voice generation failed: {exc}")

# Serve the existing web UI from the same FastAPI server.
app.mount("/", StaticFiles(directory=ROOT, html=True), name="frontend")
