from elevenlabs import generate, save  # 공식 SDK 가정
from app.core.config import settings

def generate_tts(text: str) -> str:
    """ElevenLabs TTS → 로컬 파일 경로 리턴"""
    audio = generate(text=text, api_key=settings.ELEVENLABS_API_KEY)
    path = "/tmp/tts.mp3"
    save(audio, path)
    return path
