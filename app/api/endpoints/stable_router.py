from fastapi import APIRouter
from app.schemas.atelier_schema import StableGenerationRequest, StableGenerationResponse
from app.services.atelier.stable_service import generate_stable_audio_file

router = APIRouter()

@router.post("/generate", response_model=StableGenerationResponse)
async def runway_video_endpoint(request: StableGenerationRequest):
    video_url = generate_stable_audio_file(request.prompt)
    return StableGenerationResponse(generated_natural_url=video_url)