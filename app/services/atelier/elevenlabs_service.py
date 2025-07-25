from elevenlabs import ElevenLabs
from app.core.config import settings  # .env에서 ELEVENLABS_API_KEY 불러옴

def generate_tts(speech: str, voice_id: str = "EXAVITQu4vr4xnSDxMaL", model_id: str = "eleven_multilingual_v2"):

    client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    try:
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id=model_id,
            text=speech,
            output_format="mp3_44100_128"  # 무료 사용 가능
        )
        # 결과 파일 저장
        with open("output.mp3", "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        print("✅ 음성 생성 완료! 파일: output.mp3")
        return "output.mp3"

    except Exception as e:
        print("❌ 음성 생성 실패:", e)
        raise



