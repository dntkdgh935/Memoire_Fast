from fastapi import APIRouter
from app.schemas.atelier_schema import RunwayGenerationRequest, RunwayGenerationResponse
from app.services.atelier.runway_service import generate_image_video, generate_lip_sync_video

router = APIRouter()

@router.post("/generate", response_model=RunwayGenerationResponse)
async def runway_video_endpoint(request: RunwayGenerationRequest, is_person: bool = False):
    if is_person:
        video_url = generate_lip_sync_video(request.image_url, request.tts_url)
    else:
        video_url = generate_image_video(request.image_url, request.prompt)
    return RunwayGenerationResponse(video_url=video_url)
