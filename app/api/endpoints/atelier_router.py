from fastapi import APIRouter
from app.schemas.atelier_schema import ComposeRequest, ComposeResponse
from app.services.atelier.ai_composition_service import compose_video
from app.services.atelier import textgen_service
from app.api.endpoints import text2text_router, text2image_router


router = APIRouter(prefix="/ai", tags=["AI"])
router.include_router(text2text_router.router)
router.include_router(text2image_router.router)


@router.post("/compose", response_model=ComposeResponse)
async def ai_compose(req: ComposeRequest):
    output = compose_video(
        image_url=req.image_url,
        bg_prompt=req.background_prompt,
        music_prompt=req.music_prompt,
        tts_text=req.tts_text
    )
    return ComposeResponse(video_path=output)

