# === api/endpoints/non_sync_video_router.py ===
import os
import time
from fastapi import APIRouter, HTTPException, Body
import openai
from app.schemas.atelier_schema import (
    VideoPipelineRequest, VideoPipelineResponse,
    MediaPipelineRequest, MediaPipelineResponse
)
from app.services.atelier.prompt_service import PromptRefiner
from app.services.atelier.runway_service import generate_image_video
from app.services.atelier.visionapi_service import analyze_image
from app.services.atelier.stable_service import generate_stable_audio_file
from app.services.atelier.ffmpeg_service import merge_assets

router = APIRouter()
_refiner = PromptRefiner()


def chat_with_backoff(**kwargs):
    for i in range(5):
        try:
            return openai.ChatCompletion.create(**kwargs)
        except openai.error.RateLimitError:
            # 지수 백오프
            time.sleep(2 ** i)
    raise HTTPException(status_code=429, detail="OpenAI rate limit exceeded")


@router.post("/generate-video", response_model=VideoPipelineResponse)
async def non_sync_video_pipeline(
    req: VideoPipelineRequest = Body(...)
):
    print("request : ", req)
    # 프롬프트 정제 (GPT)
    try:
        refined_prompt = _refiner.refine_video_background_prompt(req.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prompt refinement failed: {e}")
    print("refined_prompt : ", refined_prompt)

    # 이미지 경로 유효성 검사
    image_path = req.image_url
    print("image_path : ", image_path)
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=400, detail=f"Image file not found: {image_path}")

    # Runway로 영상 생성
    try:
        video_url = generate_image_video(image_path, refined_prompt)
        print("video_url : ", video_url)
        return VideoPipelineResponse(video_url=video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {e}")

