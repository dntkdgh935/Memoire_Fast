# app/services/atelier/mubert_service.py

import os
import requests
from pathlib import Path
from app.core.config import settings  # settings.MUBERT_API_KEY

def generate_music_mubert(
    prompt: str,
    duration: int = 5,
    output_path: str = "mubert_music.mp3"
) -> str:
    """
    Mubert API로 자연음/배경음 생성 후 MP3로 저장
    Returns: 저장된 파일 경로
    """
    url = "https://api.mubert.com/v1/generate_stream"
    headers = {"Authorization": f"Bearer {settings.MUBERT_API_KEY}"}
    json = {
        "prompt": prompt,
        "length": duration  # 초 단위
    }

    resp = requests.post(url, json=json, headers=headers, timeout=60)
    resp.raise_for_status()

    out = Path(output_path)
    out.write_bytes(resp.content)
    return str(out)
