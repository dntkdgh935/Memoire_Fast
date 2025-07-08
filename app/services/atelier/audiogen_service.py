import requests
from app.core.config import settings

def generate_music(prompt: str) -> str:
    """AudioGen (Mubert 등) 호출 → 음악 파일 경로/URL 리턴"""
    # 가정: POST → { "audio_url": ... }
    resp = requests.post(
        "https://api.audiogen.example/v1/generate",
        headers={"api-key": settings.AUDIOGEN_API_KEY},
        json={"prompt": prompt}
    )
    return resp.json()["audio_url"]
