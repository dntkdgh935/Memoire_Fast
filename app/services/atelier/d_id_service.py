import requests
from app.core.config import settings

def generate_facial_animation(image_url: str) -> str:
    """D-ID API에 이미지 URL 보내고, 애니메이션 영상 URL을 리턴"""
    resp = requests.post(
        "https://api.d-id.com/talks",
        headers={"Authorization": f"Bearer {settings.D_ID_API_KEY}"},
        json={
            "source_url": image_url,
            "driver_url": "...",  # 사용할 드라이버 영상
        }
    )
    data = resp.json()
    return data["result_url"]
