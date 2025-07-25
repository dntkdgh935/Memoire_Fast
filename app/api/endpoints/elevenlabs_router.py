from fastapi import APIRouter
from app.schemas.atelier_schema import TtsGenerateRequest, TtsGenerateResponse
from app.services.atelier.elevenlabs_service import generate_tts

router = APIRouter()

@router.post("/generate", response_model=TtsGenerateResponse)
async def generate_tts_endpoint(req: TtsGenerateRequest):
    result_url = generate_tts(
        speech=req.speech,
        voice_id=req.voice_id,
        model_id=req.model_id,
        stability=req.stability,
        similarity_boost=req.similarity_boost,
    )
    return TtsGenerateResponse(audio_url=f"/upload_files/tts/{result_url}")