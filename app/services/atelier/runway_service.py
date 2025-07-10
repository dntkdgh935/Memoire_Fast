# runway_service.py

import requests
import os
from app.core.config import settings
from runwayml import RunwayML, TaskFailedError

client = RunwayML(api_key=settings.RUNWAY_API_KEY)

def upload_image_asset(image_url: str):
    """이미지 URL을 업로드해 asset_id 리턴"""
    resp = client.media.upload.create(
        file_url=image_url,
        media_type="image"
    )
    return resp.asset_id

def upload_audio_asset(audio_bytes: bytes):
    """오디오 바이트를 업로드해 asset_id 리턴"""
    resp = client.media.upload.create(
        file_bytes=io.BytesIO(audio_bytes),
        media_type="audio"
    )
    return resp.asset_id

def generate_image_video(image_url: str, prompt_text: str,
                         model: str = "Gen-3 Alpha Turbo",
                         ratio: str = "1280:720",
                         duration: int = 5) -> str:
    task = client.image_to_video.create(
        model=model,
        prompt_image=image_url,
        prompt_text=prompt_text,
        ratio=ratio,
        duration=duration
    ).wait_for_task_output()
    return task["video_uri"]

def generate_lip_sync_video(image_asset_id: str, audio_asset_id: str) -> str:
    task = client.lipsync.create(
        image_assetId=image_asset_id,
        audio_assetId=audio_asset_id
    ).wait_for_task_output()
    return task["video_uri"]


