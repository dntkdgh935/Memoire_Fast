# API 키, FFmpeg 경로 등 환경변수 로딩
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(os.path.dirname(__file__), "../../.env")

class Settings(BaseSettings):
    RUNWAY_API_KEY: str
    ELEVENLABS_API_KEY: str
    MUBERT_API_KEY: str
    FFMPEG_PATH: str = "ffmpeg"  # 도커에 ffmpeg 설치시 기본 이름

    model_config = SettingsConfigDict(env_file=env_path)

settings = Settings()