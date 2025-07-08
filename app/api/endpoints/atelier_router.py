from fastapi import APIRouter
from app.schemas.atelier_schema import ComposeRequest, ComposeResponse
from app.services.atelier.ai_composition_service import compose_video

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/compose", response_model=ComposeResponse)
async def ai_compose(req: ComposeRequest):
    output = compose_video(
        image_url=req.image_url,
        bg_prompt=req.background_prompt,
        music_prompt=req.music_prompt,
        tts_text=req.tts_text
    )
    return ComposeResponse(video_path=output)
