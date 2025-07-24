from fastapi import APIRouter, Body, HTTPException
from app.schemas.atelier_schema import (
    VideoPipelineRequest   as RunwayGenerationRequest,
    VideoPipelineResponse  as RunwayGenerationResponse
)
from app.services.atelier.runway_service import generate_image_video, generate_lip_sync_video
import os

router = APIRouter()

@router.post("/generate-image-video", response_model=RunwayGenerationResponse)
async def generate_image_video_local(
    image_path: str = Body(..., embed=True),
    prompt: str = Body(..., embed=True)
):
    if not os.path.isfile(image_path):
        raise HTTPException(400, f"이미지 파일이 없습니다: {image_path}")

    try:
        url = generate_image_video(image_path, prompt)
        return RunwayGenerationResponse(video_url=url)
    except Exception as e:
        raise HTTPException(500, f"영상 생성 실패: {e}")

@router.post("/generate-lip-sync-video", response_model=RunwayGenerationResponse)
async def generate_lip_sync_video_endpoint(request: RunwayGenerationRequest):
    try:
        url = generate_lip_sync_video(request.image_url, request.tts_url)
        return RunwayGenerationResponse(video_url=url)
    except Exception as e:
        raise HTTPException(500, f"립싱크 생성 실패: {e}")
