from elevenlabs import ElevenLabs
from app.core.config import settings

def design_voice(description: str, sample_text: str = None, model_id: str = "eleven_multilingual_ttv_v2"):
    """
    Voice 디자인(미리 듣기 샘플 생성)
    Returns the first generated_voice_id.
    """
    client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
    try:
        resp = client.text_to_voice.design(
            voice_description=description,
            text=sample_text,
            model_id=model_id,
        )
        # 가장 첫 번째 프리뷰의 ID 사용
        return resp["previews"][0]["generated_voice_id"]
    except Exception as e:
        print("Voice 디자인 실패:", e)
        raise

def create_voice(name: str, description: str, generated_voice_id: str):
    """
    디자인된 샘플을 기반으로 실제 Voice 리소스 생성
    Returns the new voice_id.
    """
    client = ElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
    try:
        resp = client.text_to_voice.create(
            voice_name=name,
            voice_description=description,
            generated_voice_id=generated_voice_id,
            # labels={"age":"20s","gender":"female"}  # 필요시 추가
        )
        return resp["voice_id"]
    except Exception as e:
        print("Voice 생성 실패:", e)
        raise

if __name__ == "__main__":
    # 1) 디자인 단계
    desc = "A warm, friendly female voice in her mid-twenties."
    sample = "안녕하세요. 오늘의 뉴스를 전해드립니다."
    gen_id = design_voice(description=desc, sample_text=sample)

    # 2) 실제 리소스 생성
    voice_name = "Friendly News Anchor"
    voice_id = create_voice(name=voice_name, description=desc, generated_voice_id=gen_id)

    print(f"커스텀 음성 생성 완료! voice_id = {voice_id}")


