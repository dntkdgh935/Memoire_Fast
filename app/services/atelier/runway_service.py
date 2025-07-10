# runway_service.py
import io
import os
import base64
from app.core.config import settings
from runwayml import RunwayML, TaskFailedError

client = RunwayML(api_key=settings.RUNWAY_API_KEY)

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
    image_data_uri: str,
    prompt_text: str,
    model: str = "gen3a_turbo",
    ratio: str = "1280:720",
    duration: int = 10
) -> str:
    task = client.image_to_video.create(
        model=model,
        prompt_image=image_data_uri,  # Data URI 그대로 전달
        prompt_text=prompt_text,
        ratio=ratio,
        duration=duration
    ).wait_for_task_output()
    result = task.model_dump() if hasattr(task, 'model_dump') else (task.dict() if hasattr(task, 'dict') else task)
    # output 키가 비디오 URI 리스트 또는 문자열로 반환됨
    output = result.get('output') if isinstance(result, dict) else None
    if isinstance(output, list) and output:
        return output[0]
    if isinstance(output, str):
        return output
    raise RuntimeError(f"No video URI found in TaskRetrieveResponse; available keys: {list(result.keys())}")

BASE_DIR = os.path.dirname(__file__)

def start():
    print("▶️ start() 진입했습니다")
    image_path = os.path.join(BASE_DIR, ".jpg")
    prompt = "저 펭귄 케릭터가 여유롭게 차와 과자를 먹는 영상 만들어줘"

    print(f"image_path: {image_path} (존재: {os.path.isfile(image_path)})")
    if not os.path.isfile(image_path):
        print("❌ 파일을 찾을 수 없습니다.")
        return

    # 1) 로컬 파일 → Base64 Data URI 변환
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    data_uri = f"data:image/jpeg;base64,{b64}"
    print("✅ Data URI 생성, 길이:", len(data_uri))

    # 2) 바로 비디오 생성 호출
    print("비디오 생성 파라미터:", {
        "model": "gen3a_turbo",
        "ratio": "1280:768",
        "duration": 10
    })
    try:
        uri = generate_image_video(
            image_data_uri=data_uri,
            prompt_text=prompt,
            model="gen3a_turbo",
            ratio="1280:768",
            duration=10
        )
        print("✅ 비디오 생성 완료! URI:", uri)
    except TaskFailedError as e:
        print("❌ Runway 작업 실패:", e)
    except Exception as e:
        print("❌ 예기치 않은 오류 발생:", e)

if __name__ == "__main__":
    start()