# API 키, FFmpeg 경로 등 환경변수 로딩

from pydantic import BaseSettings

class Settings(BaseSettings):
    D_ID_API_KEY: str
    RUNWAY_API_KEY: str
    AUDIOGEN_API_KEY: str
    ELEVENLABS_API_KEY: str
    FFMPEG_PATH: str = "ffmpeg"  # 도커에 ffmpeg 설치시 기본 이름

    class Config:
        env_file = ".env"

settings = Settings()