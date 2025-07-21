from fastapi import APIRouter, HTTPException
from app.schemas.atelier_schema import OpenaiGenerationRequest
from app.services.atelier.prompt_service import PromptRefiner
from app.schemas.atelier_schema import PromptRefinementResponse

router = APIRouter()
_refiner = PromptRefiner()

@router.post("/refine-prompts", response_model=PromptRefinementResponse)
async def refine_prompts(req: OpenaiGenerationRequest):
    try:
        return PromptRefinementResponse(
            tts_prompt               = _refiner.refine_tts_prompt(req.tts_raw),
            video_person_prompt      = _refiner.refine_video_person_prompt(req.video_person_raw),
            video_noperson_prompt    = _refiner.refine_video_background_prompt(req.video_noperson_raw),
            image_prompt             = _refiner.refine_image_prompt(req.image_raw),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"프롬프트 정제 실패: {e}")
