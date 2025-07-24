# runway_service.py
import io
import os
import base64
import requests
import uuid
from pathlib import Path
from app.core.config import settings
from runwayml import RunwayML, TaskFailedError

client = RunwayML(api_key=settings.RUNWAY_API_KEY)

def _download_if_url(src: str, dest: Path) -> Path:
    """
    src가 URL이면 다운로드 → dest에 저장.
    src가 로컬 파일 경로면 그대로 Path(src) 리턴.
    """
    if src.startswith(("http://", "https://")):
        resp = requests.get(src, stream=True)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest
    return Path(src)

def upload_image_asset(image_url: str):
    resp = client.media.upload.create(
        file_url=image_url,
        media_type="image"
    )
    return resp.asset_id

def upload_audio_asset(audio_bytes: bytes):
    resp = client.media.upload.create(
        file_bytes=io.BytesIO(audio_bytes),
        media_type="audio"
    )
    return resp.asset_id

def generate_lip_sync_video(image_asset_id: str, audio_asset_id: str) -> str:
    task = client.lipsync.create(
        image_assetId=image_asset_id,
        audio_assetId=audio_asset_id
    ).wait_for_task_output()
    return task["video_uri"]

client = RunwayML(api_key=settings.RUNWAY_API_KEY)

def generate_image_video(
    image_path_or_uri: str,
    prompt_text: str,
    model: str = "gen3a_turbo",
    ratio: str = "1280:768",
    duration: int = 10
) -> str:
    if os.path.isfile(image_path_or_uri):
        # 로컬 파일이라면 base64 data URI 로 변환
        ext = image_path_or_uri.split(".")[-1]
        with open(image_path_or_uri, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        prompt_image = f"data:image/{ext};base64,{b64}"
    else:
        # data URI 혹은 원격 URL 그대로 쓰기
        prompt_image = image_path_or_uri


    task = client.image_to_video.create(
        model=model,
        prompt_image=prompt_image,
        prompt_text=prompt_text,
        ratio=ratio,
        duration=duration
    ).wait_for_task_output()

    result = (
        task.model_dump()
        if hasattr(task, "model_dump") else
        (task.dict() if hasattr(task, "dict") else task)
    )
    output = result.get("output") if isinstance(result, dict) else None

    if isinstance(output, list) and output:
        remote_url = output[0]
    elif isinstance(output, str):
        remote_url = output
    else:
        raise RuntimeError(f"No video URI in Runway response: {result}")

    output_dir = Path("C:/upload_files/memory_video")
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.mp4"
    local_path = output_dir / filename
    _download_if_url(remote_url, local_path)

    return f"/memory_video/{filename}"
