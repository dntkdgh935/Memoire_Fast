import uuid
from pathlib import Path
from elevenlabs import ElevenLabs
from app.core.config import settings


def generate_tts(speech: str, voice_id: str, model_id: str, stability: float, similarity_boost: float) -> str:

    client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)

    voice_settings = {
        "stability": stability,
        "similarity_boost": similarity_boost
    }

    try:
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            model_id=model_id,
            text=speech,
            voice_settings=voice_settings,
            output_format="mp3_44100_128"
        )

        out_dir = Path("C:/upload_files/tts")
        out_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4().hex}.mp3"
        file_path = out_dir / filename

        with open(file_path, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)

        return filename

    except Exception as e:
        print("❌ 음성 생성 실패:", e)
        raise



