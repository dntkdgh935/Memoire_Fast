# app/services/tarot/tarot_service.py

from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_reading(spread_type: str, cards: list[dict]) -> str:
    """
    신비로운 마법사 스타일로 AI 타로 리딩 생성 (동기 방식)
    """
    # 카드 이름만 쉼표로 이어 붙이기
    card_names = ", ".join([c["name"] for c in cards])

    # 마법사 스타일 프롬프트
    prompt = f"""
너는 고대의 신비로운 마법사로, 타로 카드의 기운을 해석해주는 예언자다.
지금 사용자가 {spread_type}장의 카드를 뽑았으며, 그 목록은 다음과 같다: {card_names}

각 카드에 대해 다음 규칙을 지켜 서술하라:
- 카드 이름을 문장 안에 자연스럽게 녹여서 사용하라
- 번호, 기호(**, -, 1., 등) 없이 자연스러운 단락으로 서술하라
- 각 카드 설명은 2~3문장으로 조용하고 예언자처럼 말하라
- 마지막엔 전체 흐름을 설명하는 '전체 리딩' 문단을 덧붙여라 (줄바꿈 포함, 4~5문장)

출력은 순수한 자연어로만 구성하라. HTML, Markdown, 리스트, 기호 없이 순수하게.
    """.strip()

    # GPT 요청
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 조용하고 신비로운 고대의 마법사다. 타로의 상징과 기운을 해석하여 말해준다."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1200,  # ← 여기서 길이 제한 조절
        temperature=0.9   # 약간 더 창의적인 말투 허용
    )

    return resp.choices[0].message.content.strip()