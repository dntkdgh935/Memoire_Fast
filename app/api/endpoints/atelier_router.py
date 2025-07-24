from fastapi import APIRouter
from app import (
    elevenlabs_router,
    runway_router,
    openai_router,
    ffmpeg_router,
    vertex_router,
    stable_router,
    vision_router,
    non_sync_video_router,
)
router = APIRouter(prefix="/atelier", tags=["Atelier"])



router.include_router(elevenlabs_router, prefix="/tts")
router.include_router(runway_router, prefix="/runway")
router.include_router(openai_router, prefix="/openai")
router.include_router(ffmpeg_router, prefix="/ffmpeg")
router.include_router(vertex_router, prefix="/image-1")
router.include_router(stable_router, prefix="/stable")
router.include_router(vision_router, prefix="/vision")
router.include_router(non_sync_video_router, prefix="/video")



