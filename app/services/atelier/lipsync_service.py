import os
import time
import uuid
import requests
from io import BytesIO
from pathlib import Path


HEADERS  = {
    "x-rapidapi-key": "a469bc4124msh2a54debc3d2f590p1360d6jsna25f53b5c11d",
    "x-rapidapi-host": "runwayml-api.p.rapidapi.com",
    "Content-Type": "application/json"
}

FILE_HEADERS = {
    "x-rapidapi-key": "a469bc4124msh2a54debc3d2f590p1360d6jsna25f53b5c11d",
    "x-rapidapi-host": "runwayml-api.p.rapidapi.com"
}

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

# ✅ MIME 타입 자동 판별
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

def upload_asset(src: str) -> str:
    print(src)

    if src.startswith(("http://", "https://")):
        resp = requests.get(src, stream=True)
        resp.raise_for_status()
        data = resp.content
        filename = os.path.basename(src)
    else:
        path = Path(src)
        if not path.is_file():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")
        data = path.read_bytes()
        filename = path.name

    mime = get_mime_type(filename)

    files = {
        "file": (filename, BytesIO(data), mime)
    }

    res = requests.post(
        "https://runwayml-api.p.rapidapi.com/assets/",
        headers=FILE_HEADERS,
        files=files
    )
    res.raise_for_status()
    asset_id = res.json().get("id")
    if not asset_id:
        raise RuntimeError(f"Asset upload 실패, 응답: {res.text}")
    return asset_id

    # if not res.ok:
    #     print("❌ Asset upload failed:", res.status_code, res.text)
    # res.raise_for_status()
    #
    # asset_id = res.json()["id"]
    # print(f"✅ asset uploaded. id={asset_id}")
    # return asset_id


def generate_lip_sync_video(image_url: str, audio_url: str) -> str:
    image_asset_id = upload_asset(image_url)
    audio_asset_id = upload_asset(audio_url)

    payload = {
        "image_assetId": image_asset_id,
        "audio_assetId": audio_asset_id
    }

    print("🔁 립싱크 작업 생성 요청 중...")
    res = requests.post("https://runwayml-api.p.rapidapi.com/v1/runwayml/lipsync/create", headers=HEADERS, json=payload)

    if res.status_code != 200:
        raise RuntimeError(f"❌ 작업 생성 실패: {res.status_code}, {res.text}")

    res.raise_for_status()
    task_id = res.json()["id"]
    print("✅ 작업 생성됨. task_id:", task_id)

    print("⏳ 결과 대기 중...")
    while True:
        task_res = requests.get(f"https://runwayml-api.p.rapidapi.com/v1/runwayml/tasks/{task_id}", headers=HEADERS)
        task_data = task_res.json()
        status = task_data.get("status")
        print(f"🔄 현재 상태: {status}")

        if status == "SUCCEEDED":
            video_url = task_data["artifacts"][0]["url"]
            print("✅ 생성 완료! 영상 URL:", video_url)
            break
        elif status == "FAILED":
            raise RuntimeError(f"❌ 생성 실패: {task_data.get('error', {})}")

        time.sleep(5)

    output_dir = Path("C:/upload_files/memory_video")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.mp4"
    local_path = output_dir / filename

    _download_if_url(video_url, local_path)

    print(f"📥 영상 저장 완료: {local_path}")
    return f"/memory_video/{filename}"


if __name__ == "__main__":
    img_url = "http://localhost:8080/upload_files/memory_img/2dbfff69-67e6-40c2-97e6-48214e48496c.jpg"
    try:
        aid = upload_asset(img_url)
        print("업로드된 assetId:", aid)
    except Exception as e:
        print("업로드 중 예외 발생:", e)