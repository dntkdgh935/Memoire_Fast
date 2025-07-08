import requests
from app.core.config import settings

def generate_background(prompt: str) -> str:
    """Runway Gen-2 API 호출 → 영상 URL 리턴"""
    resp = requests.post(
        "https://api.runwayml.com/v1/videos",
        headers={"Authorization": f"Bearer {settings.RUNWAY_API_KEY}"},
        json={"prompt": prompt}
    )
    return resp.json()["video_url"]
