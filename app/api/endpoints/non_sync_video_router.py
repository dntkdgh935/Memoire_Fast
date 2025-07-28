# === api/endpoints/non_sync_video_router.py ===
import os
import time
import requests
from io import BytesIO
from fastapi import APIRouter, HTTPException, Body
import openai
from PIL import Image
from app.schemas.atelier_schema import (
    VideoPipelineRequest, VideoPipelineResponse
)
from app.services.atelier.prompt_service import PromptRefiner
from app.services.atelier.runway_service import generate_image_video

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
        best_ratio = get_best_ratio(image_path)
        print("best_ratio:", best_ratio)
        video_url = generate_image_video(image_path, refined_prompt, best_ratio)
        print("video_url : ", video_url)
        return VideoPipelineResponse(video_url=video_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video generation failed: {e}")


def get_best_ratio(image_path_or_uri: str) -> str:
    print("start ratio>>>>>>>>>>>>")
    if os.path.isfile(image_path_or_uri):
        with Image.open(image_path_or_uri) as img:
            w, h = img.size
    else:
        response = requests.get(image_path_or_uri)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        w, h = img.size

    ratio = w / h

    if ratio < 1:
        # 세로가 더 길면 세로형
        return "768:1280"
    else:
        # 가로가 더 길거나 정사각형에 가까우면 가로형
        return "1280:768"
