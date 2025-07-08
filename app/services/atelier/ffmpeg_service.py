import subprocess
from app.core.config import settings

def merge_assets(
    face_video_url: str,
    bg_video_url: str,
    music_url: str,
    tts_path: str,
    output_path: str
) -> str:
    """
    1) 각 URL→로컬 다운로드
    2) ffmpeg로 레이어 합성(예: 얼굴 영상 위에 배경 합치기)
    3) 배경 음악+TTS 합치기
    """
    # (다운로드 로직 생략)
    cmd = [
        settings.FFMPEG_PATH,
        "-i", "face.mp4",
        "-i", "bg.mp4",
        "-filter_complex", "overlay=0:0",
        "-i", "music.mp3",
        "-i", tts_path,
        "-map", "0:v", "-map", "2:a", "-map", "3:a",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd, check=True)
    return output_path
