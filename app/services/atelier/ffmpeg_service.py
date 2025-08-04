import uuid
import shutil
import subprocess
import requests
import tempfile
from pathlib import Path



def _download_if_url(path_or_url: str, target_path: Path) -> Path:
    print(f"[🔽] 다운로드 또는 경로 확인 중: {path_or_url}")

    # 1) localhost URL일 경우 → 로컬 경로로 변환
    if path_or_url.startswith("http://localhost:8000"):
        path_or_url = path_or_url.replace("http://localhost:8000/upload_files", "")

    if path_or_url.startswith("/"):
        full_path = Path("C:/upload_files") / path_or_url.lstrip("/")
        if full_path.exists():
            return full_path
        else:
            raise FileNotFoundError(f"로컬 경로가 존재하지 않음: {full_path}")

    # 3) 외부 URL인 경우 다운로드
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        with requests.get(path_or_url, stream=True) as r:
            r.raise_for_status()
            with open(target_path, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        return target_path

    # 4) 로컬 경로로 직접 주어진 경우
    path = Path(path_or_url)
    if path.exists():
        print(f"[✅] 직접 지정된 로컬 경로 사용: {path}")
        return path
    else:
        raise FileNotFoundError(f"지정된 경로 없음: {path}")


def merge_assets(video_url: str, tts_path: str) -> str:
    print("🛠 merge_assets 시작")
    tmp_dir = Path(tempfile.mkdtemp())
    print(f"임시 디렉토리 생성됨: {tmp_dir}")

    try:
        video_file = _download_if_url(video_url, tmp_dir / "video.mp4")
        tts_file = _download_if_url(tts_path, tmp_dir / "tts.mp3")

        output_dir = Path("C:/upload_files/memory_video")
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"출력 디렉토리 준비됨: {output_dir}")

        out_name = f"{uuid.uuid4().hex}.mp4"
        output_file = output_dir / out_name
        print(f"출력 파일명: {output_file}")

        ffmpeg_path = r"C:\ffmpeg-7.1.1-essentials_build\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"

        cmd = [
            ffmpeg_path,
            "-y",
            "-i", str(video_file).replace("\\", "/"),
            "-i", str(tts_file).replace("\\", "/"),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            str(output_file).replace("\\", "/")
        ]

        print("FFmpeg 명령 실행 중...")
        print(" ".join(map(str, cmd)))
        subprocess.run(cmd, check=True)
        print("FFmpeg 실행 완료")

        return f"/memory_video/{out_name}"

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 실행 오류: {e}")
        raise

    except Exception as e:
        print(f"예외 발생: {e}")
        raise

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        print(f"임시 디렉토리 삭제 완료: {tmp_dir}")