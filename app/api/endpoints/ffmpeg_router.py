from fastapi import APIRouter
from app.schemas.atelier_schema import FfmpegGenerationRequest, FfmpegGenerationResponse
from app.services.atelier.ffmpeg_service import merge_assets

router = APIRouter()

@router.post("/generate", response_model=FfmpegGenerationResponse)
async def ffmpeg_merge_endpoint(request: FfmpegGenerationRequest):
    processed_video_url = merge_assets(request.video_url, request.tts_url)
    return FfmpegGenerationResponse(processed_video_url=processed_video_url)
