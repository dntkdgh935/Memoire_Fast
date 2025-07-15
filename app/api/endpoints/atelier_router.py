from fastapi import APIRouter
from app import (
    text2text_router,
    text2image_router,
    elevenlabs_router,
    runway_router,
    openai_router,
    ffmpeg_router,
    vertex_router
)


router = APIRouter(prefix="/ai", tags=["AI"])
router.include_router(text2text_router.router)
router.include_router(text2image_router.router)
router.include_router(elevenlabs_router.router, prefix="/tts")
router.include_router(runway_router.router, prefix="/runway")
router.include_router(openai_router.router, prefix="/openai")
router.include_router(ffmpeg_router.router, prefix="/ffmpeg")
router.include_router(vertex_router.router, prefix="/vertex")


