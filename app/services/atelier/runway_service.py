# runway_service.py
from io import BytesIO
import os
import time
import base64
import requests
import uuid
from pathlib import Path
from app.core.config import settings
from runwayml import RunwayML
import logging
from urllib.parse import urlparse
from runwayml.types.character_performance_create_params import CharacterImage, Reference


client = RunwayML(api_key=settings.RUNWAY_API_KEY)

logger = logging.getLogger(__name__)

def load_local_tts(tts_url: str) -> BytesIO:
    # URL 경로에서 순수 파일명만 뽑아내기
    fname = Path(urlparse(tts_url).path).name
    # 실제 저장된 폴더와 결합
    tts_dir = Path("C:/upload_files/tts")
    path = tts_dir / fname

    if not path.exists() or not path.is_file():
        raise RuntimeError(f"TTS 파일을 찾을 수 없습니다: {path}")

    # 로컬 파일을 바로 읽어서 BytesIO로 감쌉니다
    data = path.read_bytes()
    return BytesIO(data)

def _download_if_url(src: str, dest: Path) -> Path:
    if src.startswith(("http://", "https://")):
        resp = requests.get(src, stream=True)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        with open(dest, "wb") as f:

            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest
    return Path(src)

# def generate_lip_sync_video(image_url: str, tts_url: str) -> str:
#     logger.debug("▶▶ enter generate_lip_sync_video")
#     try:
#         character = CharacterImage(
#             image=image_url,  # str
#             name="GeneratedCharacter"
#         )
#
#         reference = Reference(
#             audio=tts_url  # str
#         )
#
#         t2 = time.perf_counter()
#         req = client.character_performance.create(
#             character=character,
#             reference=reference,
#             model="act_two",
#             ratio="832:1104",
#             timeout=180.0
#         )
#         logger.info(f"3) create() call: {time.perf_counter() - t2:.1f}s")
#
#         t3 = time.perf_counter()
#         task = req.wait_for_task_output(timeout=180.0)
#         logger.info(f"4) wait_for_task_output: {time.perf_counter() - t3:.1f}s")
#
#         if not task.output:
#             raise RuntimeError("영상 생성 실패: 출력이 없습니다.")
#
#         video_url = task.output[0]
#         output_dir = Path("C:/upload_files/memory_video")
#         output_dir.mkdir(parents=True, exist_ok=True)
#         filename = f"{uuid.uuid4().hex}.mp4"
#         local_path = output_dir / filename
#
#         resp = requests.get(video_url, timeout=(5, 30))
#         resp.raise_for_status()
#         with open(local_path, "wb") as f:
#             f.write(resp.content)
#
#         return f"/memory_video/{filename}"
#
#     except Exception:
#         logger.exception("💥 립싱크 생성 중 치명적 예외 발생")
#         raise


# def upload_image_asset(image_url: str):
#     resp = client.assets.create(
#         file_url=image_url,
#         media_type="image"
#     )
#     return resp.asset_id
#
# def upload_audio_asset(audio_bytes: bytes) -> str:
#     # 메모리 상의 오디오 바이트를 Runway에 업로드하고 asset_id 반환
#     resp = client.assets.create(
#         file_bytes=BytesIO(audio_bytes),  # 오디오 데이터
#         media_type="audio"                # 미디어 타입 지정
#     )
#     return resp.asset_id

# def generate_lip_sync_video(image_url: str, tts_url: str, ratio: str) -> str:
#     try:
#         print("▶ image_url:", image_url, "tts_url:", tts_url, "ratio:", ratio)
#         req = client.character_performance.create(
#             image=image_url,
#             audio=tts_url
#         )
#
#         task = req.wait_for_task_output(timeout=180.0)
#
#         if not task.output:
#             raise RuntimeError("영상 생성 실패: 출력 없음")
#
#         # 4) 결과 비디오 다운로드 후 로컬 저장
#         video_url = task.output[0]
#         output_dir = Path("C:/upload_files/memory_video")
#         output_dir.mkdir(parents=True, exist_ok=True)
#         filename = f"{uuid.uuid4().hex}.mp4"
#         local_path = output_dir / filename
#
#         resp = requests.get(video_url, timeout=(5, 30))
#         resp.raise_for_status()
#         with open(local_path, "wb") as f:
#             f.write(resp.content)
#
#         return f"/memory_video/{filename}"
#
#     except Exception:
#         logger.exception("💥 영상 생성 중 치명적 예외 발생")
#         raise

def generate_image_video(
    image_path_or_uri: str,
    prompt_text: str,
    ratio: str,
    model: str = "gen3a_turbo",
    duration: int = 10
) -> str:
    if os.path.isfile(image_path_or_uri):
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
