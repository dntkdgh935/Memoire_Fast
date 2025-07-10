# API 키, FFmpeg 경로 등 환경변수 로딩
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(os.path.dirname(__file__), "../../.env")

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    RUNWAY_API_KEY: str
    ELEVENLABS_API_KEY: str
    MUBERT_API_KEY: str
    VERTEX_API_KEY: str
    FFMPEG_PATH: str = "ffmpeg"  # 도커에 ffmpeg 설치시 기본 이름
    openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../.env")
        ),
        env_file_encoding="utf-8"
    )

settings = Settings()