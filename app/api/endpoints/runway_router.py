from fastapi import APIRouter
from app.schemas.atelier_schema import RunwayGenerationRequest, RunwayGenerationResponse
from app.services.atelier.runway_service import generate_image_video, generate_lip_sync_video

router = APIRouter()

@router.post("/generate-image-video", response_model=RunwayGenerationResponse)
async def generate_image_video_endpoint(request: RunwayGenerationRequest):
    video_url = generate_image_video(request.image_url, request.prompt)
    return RunwayGenerationResponse(video_url=video_url)

@router.post("/generate-lip-sync-video", response_model=RunwayGenerationResponse)
async def generate_lip_sync_video_endpoint(request: RunwayGenerationRequest):
    video_url = generate_lip_sync_video(request.image_url, request.tts_url)
    return RunwayGenerationResponse(video_url=video_url)
