from fastapi import APIRouter, HTTPException, Form
from app.schemas.atelier_schema import (
    TtsConfigRequest, TtsConfigResponse )
from app.services.atelier.prompt_service import PromptRefiner
from app.services.atelier.voiceId_service import sanitize_voice_id
import logging

logger = logging.getLogger(__name__)


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
    logger.info("▶▶ generate-tts-config called, payload: %r", req)

    try:
        cfg: dict = _refiner.refine_tts_config(
            script=req.script,
            voice_gender=req.voiceGender
        )
        try:
            cfg["voice_id"] = sanitize_voice_id(cfg["voice_id"])
        except ValueError as e:
            logger.warning(f"⚠️ 잘못된 voice_id 입력됨: {cfg['voice_id']}")
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(502, f"TTS 설정 분석 실패: {e}")

    logger.info("▶▶ refine_tts_config returned: %r", cfg)

    return TtsConfigResponse(
        voice_id=cfg["voice_id"],
        model_id=cfg["model_id"],
        stability=cfg["stability"],
        similarity_boost=cfg["similarity_boost"],
    )