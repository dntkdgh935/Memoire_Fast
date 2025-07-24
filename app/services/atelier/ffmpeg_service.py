# app/services/atelier/ffmpeg_service.py

import os
import subprocess
import requests
import tempfile
from pathlib import Path
from app.core.config import settings

def _download_if_url(src: str, dest: Path) -> Path:
    """
    src가 URL이면 다운로드 → dest에 저장.
    src가 로컬 파일 경로면 그대로 Path(src) 리턴.
    """
    if src.startswith(("http://", "https://")):
        resp = requests.get(src, stream=True)
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return dest
    return Path(src)

def merge_assets(video_url: str, tts_path: str,
                 output_path: str = "final.mp4") -> str:
    tmp_dir = Path(tempfile.mkdtemp())
    video_file = _download_if_url(video_url, tmp_dir / "video.mp4")
    tts_file = Path(tts_path)

    # 2) 로컬 저장 폴더 준비
    output_dir = Path("C:/upload_files/memory_video")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 3) 고유 파일명 생성
    out_name = f"{uuid.uuid4().hex}.mp4"
    output_path = output_dir / out_name

    cmd = [settings.FFMPEG_PATH, "-y", "-i", str(video_file), "-i", str(music_file)]

    if tts_file:
        # TTS 있음 → 배경음+TTS 합성 후 비디오에 붙임
        cmd += [
            "-i", str(tts_file),
            "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first[aud]",
            "-map", "0:v", "-map", "[aud]"
        ]
    else:
        # TTS 없음 → 배경음만 비디오에 붙임
        cmd += [
            "-map", "0:v", "-map", "1:a"
        ]
    cmd += ["-shortest", str(output_path)]

    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return f"/memory_video/{filename}"