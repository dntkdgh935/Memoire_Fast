# API 키, FFmpeg 경로 등 환경변수 로딩
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = os.path.join(os.path.dirname(__file__), "../../.env")

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    RUNWAY_API_KEY: str
    ELEVENLABS_API_KEY: str
    USEAPI_TOKEN: str
    RUNWAY_EMAIL: str
    RUNWAY_PASSWORD: str


    model_config = SettingsConfigDict(
        env_file=os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../.env")
        ),
        env_file_encoding="utf-8"
    )

settings = Settings()