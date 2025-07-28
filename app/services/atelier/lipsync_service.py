import os
import time
import uuid
import requests
from app.core.config import settings
from io import BytesIO
import tempfile
import shutil
from pathlib import Path

HEADERS = {
    "Authorization": f"Bearer {settings.USEAPI_TOKEN}",
    "Content-Type":  "application/json"
}

FILE_HEADERS = {
    "x-rapidapi-key": "a469bc4124msh2a54debc3d2f590p1360d6jsna25f53b5c11d",
    "x-rapidapi-host": "runwayml-api.p.rapidapi.com"
}

def link_runway_account():
    url = f"https://api.useapi.net/v1/runwayml/accounts/{settings.RUNWAY_EMAIL}"

    body = {
        "email": settings.RUNWAY_EMAIL,
        "password": settings.RUNWAY_PASSWORD,
        "maxJobs": 1
    }

    try:
        resp = requests.post(url, headers=HEADERS, json=body)
        # 409는 이미 연동 상태이므로 무시
        if resp.status_code == 409:
            print("ℹ️ RunwayML 계정이 이미 연동되어 있습니다.")
            return
        resp.raise_for_status()
        print("✅ RunwayML 계정 연동 완료:", resp.json())
    except requests.exceptions.HTTPError as e:
        # 409가 아닌 에러는 그대로
        if e.response.status_code != 409:
            raise

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

def download_or_local(src: str, dest: Path) -> Path:
    # 1) localhost:8000/upload_files → C:/upload_files
    if src.startswith("http://localhost:8000/upload_files"):
        rel = src.replace("http://localhost:8000/upload_files", "")
        full = Path("C:/upload_files") / rel.lstrip("/")
        if full.exists():
            return full
        raise FileNotFoundError(full)

    if src.startswith("/upload_files/"):
        full = Path("C:/upload_files") / src.lstrip("/")
        if full.exists():
            return full
        raise FileNotFoundError(full)

        # 3) 그 외 URL이면 다운로드
    if src.startswith(("http://", "https://")):
        dest.parent.mkdir(parents=True, exist_ok=True)
        with requests.get(src, stream=True) as r:
            r.raise_for_status()
            with open(dest, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        return dest

        # 4) 로컬 경로
    full = Path(src)
    if full.exists():
        return full
    raise FileNotFoundError(src)


def get_mime_type(file_path: str) -> str:
    if file_path.endswith(".jpg") or file_path.endswith(".jpeg"):
        return "image/jpeg"
    elif file_path.endswith(".png"):
        return "image/png"
    elif file_path.endswith(".mp3"):
        return "audio/mpeg"
    elif file_path.endswith(".wav"):
        return "audio/wav"
    else:
        raise ValueError("지원되지 않는 파일 형식입니다.")

def upload_asset(src: bytes, name: str) -> str:
    print("asset 시작")
    mine = get_mime_type(name)

    api_url = f"https://api.useapi.net/v1/runwayml/assets/?name={name}"
    headers = {
        "Authorization": f"Bearer {settings.USEAPI_TOKEN}",
        "Content-Type": mine,
    }

    resp = requests.post(api_url, headers=headers, data=src)
    resp.raise_for_status()
    data = resp.json()

    asset_key = data.get("assetId")
    if not asset_key:
        raise RuntimeError(f"Asset 업로드 실패: {data}")
    print(f"✅ Asset 업로드 완료: {asset_key}")
    return asset_key

def poll_lipsync_task(task_id: str,
                      timeout: int = 300,
                      interval: int = 5) -> str:
    """
    taskId가 SUCCEEDED 상태가 될 때까지 최대 timeout초 동안
    interval초 간격으로 상태를 조회합니다.
    성공 시 artifacts[0]['url'] 을 반환, 실패 시 예외를 던집니다.
    """
    start = time.time()
    url   = f"https://api.useapi.net/v1/runwayml/tasks/{task_id}"
    while True:
        if time.time() - start > timeout:
            raise TimeoutError(f"Lip‑sync polling timed out after {timeout}s")

        res = requests.get(url, headers=HEADERS)
        res.raise_for_status()
        data = res.json()
        status = data.get("status")

        if status == "SUCCEEDED":
            artifacts = data.get("artifacts", [])
            if artifacts:
                return artifacts[0]["url"]
            raise RuntimeError("Lip‑sync succeeded but no artifacts found")

        if status == "FAILED":
            err = data.get("error") or data
            raise RuntimeError("Lip‑sync failed:", err)

        # 아직 진행 중
        print(f"🔄 상태 {status}. 다음 확인까지 {interval}s 대기")
        time.sleep(interval)

def generate_lip_sync_video(image_url: str, audio_url: str) -> str:
    print("image_url", image_url, "audio_url", audio_url)
    link_runway_account()

    img_bytes = requests.get(image_url).content
    image_asset = upload_asset(img_bytes, name="face.png")
    print("image_asset 완료")

    tmp = Path(tempfile.mkdtemp())
    audio_file = download_or_local(audio_url, tmp / "tts.mp3")
    audio_bytes = audio_file.read_bytes()
    audio_asset = upload_asset(audio_bytes, name=audio_file.name)
    print("audio_asset 완료")

    payload = {
        "image_assetId": image_asset,
        "audio_assetId": audio_asset
    }

    print("🔁 립싱크 작업 생성 요청 중...")
    res = requests.post(
        "https://api.useapi.net/v1/runwayml/lipsync/create",
        headers=HEADERS,
        json=payload
    )

    # 디버그용: 응답 상태와 본문을 먼저 찍습니다
    print(f"💬 립싱크 응답 상태: {res.status_code}")
    print(f"💬 립싱크 응답 본문: {res.text}")

    res.raise_for_status()
    task_id = res.json()["taskId"]
    print("✅ 작업 생성됨. taskId:", task_id)

    print("⏳ Lip‑sync 완료 대기 중…")
    video_url = poll_lipsync_task(task_id, timeout=180, interval=5)

    output_dir = Path("C:/upload_files/memory_video")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.mp4"
    local_path = output_dir / filename

    _download_if_url(video_url, local_path)

    print(f"📥 영상 저장 완료: {local_path}")
    return f"/memory_video/{filename}"
