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

def merge_assets(
    video_url: str,
    tts_path: str | None,
    output_path: str = "final.mp4"
) -> str:
    """
    1) video_url, music_url, tts_path(선택적)를 로컬 파일로 준비
    2) ffmpeg -filter_complex 로 영상/오디오 합성
    3) output_path 리턴
    """
    # 1) 임시 파일 준비
    tmp_dir = Path(tempfile.mkdtemp())
    video_file = _download_if_url(video_url, tmp_dir / "video.mp4")
    # tts_path는 이미 로컬 경로라 가정. 없으면 None
    tts_file = Path(tts_path) if tts_path else None

    # 2) ffmpeg 커맨드 조립
    # - 비디오 트랙: video_file
    # - 오디오 트랙: background music + (tts가 있으면) tts 믹스
    cmd = [
        settings.FFMPEG_PATH,
        # 입력: video
        "-i", str(video_file),
        # 입력: music
    ]
    if tts_file:
        # 입력: tts
        cmd += ["-i", str(tts_file)]
        # 오디오 믹스 필터: music(0:a) + tts(1:a)
        # filter_complex 인덱스는 video=0, music=1, tts=2
        cmd += [
            "-filter_complex",
            "[1:a][2:a]amix=inputs=2:duration=first[aud]",
            # 비디오는 그대로 0:v, 믹스된 오디오는 [aud]
            "-map", "0:v",
            "-map", "[aud]",
        ]
    else:
        # tts 없으면 music만 사용
        cmd += [
            "-map", "0:v",
            "-map", "1:a",
        ]

    # 공통 옵션: 영상 길이에 맞춰 가장 짧은 트랙 기준
    cmd += ["-shortest", str(output_path)]

    # 3) ffmpeg 실행
    subprocess.run(cmd, check=True)

    # 4) 결과 리턴
    return output_path
