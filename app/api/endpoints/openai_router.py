from fastapi import APIRouter, HTTPException, Form
from app.schemas.atelier_schema import (
    OpenaiGenerationRequest, PromptRefinementResponse,
    TtsConfigRequest, TtsConfigResponse )
from app.services.atelier.prompt_service import PromptRefiner

router = APIRouter()
_refiner = PromptRefiner()

# 이미지 생성 프롬프트 생성 부분
@router.post("/generate-image-prompt")
async def generate_image_prompt(image_raw: str = Form(...)):
    try:
        prompt = _refiner.refine_image_prompt(image_raw)
        print("generated image prompt", prompt)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이미지 프롬프트 정제 실패: {e}")

# 3. TTS(음성 합성) 프롬프트
@router.post("/generate-tts-prompt")
async def generate_tts_prompt(tts_raw: str = Form(...)):
    try:
        prompt = _refiner.refine_tts_prompt(tts_raw)
        print("generated tts prompt", prompt)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS 프롬프트 정제 실패: {e}")

# 배경 중심 영상 프롬프트 생성 부분
@router.post("/generate-video-background-prompt")
async def generate_video_background_prompt(video_noperson_raw: str = Form(...)):
    try:
        prompt = _refiner.refine_video_background_prompt(video_noperson_raw)
        print("generated video background prompt", prompt)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"비디오(배경) 프롬프트 정제 실패: {e}")

# 자연음 생성 부분
@router.post("/generate-sound-prompt")
async def generate_sound_prompt(image_raw: str = Form(...)):
    try:
        prompt = _refiner.generate_nature_sound_prompt(image_raw)
        print("generated sound prompt", prompt)
        return {"prompt": prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"자연음 프롬프트 생성 실패: {e}")

# eleven 프롬프트 생성 부분
@router.post(
    "/generate-tts-config",
    response_model=TtsConfigResponse,
)
async def generate_tts_config(req: TtsConfigRequest):
    try:
        cfg: dict = _refiner.refine_tts_config(
            script=req.script,
            voice_gender=req.voice_gender
        )
    except Exception as e:
        raise HTTPException(502, f"TTS 설정 분석 실패: {e}")

    return TtsConfigResponse(
        voice_id=cfg["voice_id"],
        model_id=cfg["model_id"],
        pitch=cfg["pitch"],
        rate=cfg["rate"],
    )