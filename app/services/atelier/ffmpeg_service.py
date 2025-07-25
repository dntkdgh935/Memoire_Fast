# app/services/atelier/ffmpeg_service.py

import os
import uuid
import shutil
import subprocess
import requests
import tempfile
from pathlib import Path
from app.core.config import settings



def _download_if_url(src: str, dest: Path) -> Path:
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
    try:
        # 영상과 TTS 오디오 다운로드 또는 경로 처리
        video_file = _download_if_url(video_url, tmp_dir / "video.mp4")
        tts_file = _download_if_url(tts_path, tmp_dir / "tts.mp3")

        # 결과 저장 디렉토리 생성
        output_dir = Path("C:/upload_files/memory_video")
        output_dir.mkdir(parents=True, exist_ok=True)

        # 고유한 파일명 생성
        out_name = f"{uuid.uuid4().hex}.mp4"
        output_file = output_dir / out_name

        # FFmpeg 명령어 생성
        cmd = [
            settings.FFMPEG_PATH,
            "-y",
            "-i", str(video_file),
            "-i", str(tts_file),
            "-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first[aud]",
            "-map", "0:v",
            "-map", "[aud]",
            "-shortest",
            str(output_file)
        ]

        # FFmpeg 실행
        subprocess.run(cmd, check=True)

        # 결과 파일 경로 리턴 (URL 용)
        return f"/memory_video/{out_name}"

    finally:
        # 임시 파일 정리
        shutil.rmtree(tmp_dir, ignore_errors=True)