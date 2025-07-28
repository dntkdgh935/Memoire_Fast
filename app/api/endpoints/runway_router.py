import os
import requests
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, HTTPException, Body
from app.services.atelier.lipsync_service import generate_lip_sync_video
from app.schemas.atelier_schema import VideoPipelineResponse, LipSyncResponse

router = APIRouter()

@router.post("/lipsync", response_model=LipSyncResponse)
async def create_lip_sync_video(
    image_url: str = Body(..., embed=True),
    audio_url: str = Body(..., embed=True),
):
    try:
        print("image_url", image_url, "audio_url", audio_url)
        video_url = generate_lip_sync_video(image_url, audio_url)
        return LipSyncResponse(video_url=video_url)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# def get_best_ratio(image_path_or_uri: str) -> str:
#     print("start ratio>>>>>>>>>>>>")
#     if os.path.isfile(image_path_or_uri):
#         with Image.open(image_path_or_uri) as img:
#             w, h = img.size
#     else:
#         response = requests.get(image_path_or_uri)
#         response.raise_for_status()
#         img = Image.open(BytesIO(response.content))
#         w, h = img.size
#
#     ratio = w / h
#
#     if ratio < 1:
#         # 세로가 더 길면 세로형
#         return "768:1280"
#     else:
#         # 가로가 더 길거나 정사각형에 가까우면 가로형
#         return "1280:768"
