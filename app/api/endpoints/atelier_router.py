from fastapi import APIRouter
from app import (
    elevenlabs_router,
    runway_router,
    openai_router,
    ffmpeg_router,
    vertex_router,
    stable_router,
)
router = APIRouter(prefix="/atelier", tags=["Atelier"])



router.include_router(elevenlabs_router, prefix="/tts")
router.include_router(runway_router, prefix="/runway")
router.include_router(openai_router, prefix="/openai")
router.include_router(ffmpeg_router, prefix="/ffmpeg")
router.include_router(vertex_router, prefix="/image-1")
router.include_router(stable_router, prefix="/stable")


# ➡️ {'POST'} /atelier/tts/generate
# ➡️ {'POST'} /atelier/runway/generate
# ➡️ {'POST'} /atelier/openai/generate
# ➡️ {'POST'} /atelier/ffmpeg/generate
# ➡️ {'POST'} /atelier/image-1/generate
# ➡️ {'POST'} /atelier/stable/generate



