from fastapi import APIRouter
from app.schemas.atelier_schema import ElevenlabsGenerationRequest, ElevenlabsGenerationResponse
from app.services.atelier.elevenlabs_service import generate_tts

router = APIRouter()

@router.post("/generate", response_model=ElevenlabsGenerationResponse)
async def generate_tts_endpoint(request: ElevenlabsGenerationRequest):
    audio_url = generate_tts(request.text)
    return ElevenlabsGenerationResponse(audio_url=audio_url)
