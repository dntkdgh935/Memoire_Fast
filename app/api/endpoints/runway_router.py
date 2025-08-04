from fastapi import APIRouter, HTTPException, Body
from app.services.atelier.lipsync_service import generate_lip_sync_video
from app.schemas.atelier_schema import LipSyncResponse

router = APIRouter()

@router.post("/lipsync", response_model=LipSyncResponse)
async def create_lip_sync_video(
    image_url: str = Body(..., embed=True),
    audio_url: str = Body(..., embed=True),
):
    try:
        print("image_url", image_url, "audio_url", audio_url)
        video_url = generate_lip_sync_video(image_url, audio_url)
        print("video_url", video_url)
        return LipSyncResponse(video_url=video_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

