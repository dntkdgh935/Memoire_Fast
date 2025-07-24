# app/services/tarot/tarot_service.py

from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_reading(spread_type: str, cards: list[dict]) -> str:
    """
    동기 방식으로 AI 리딩을 생성합니다.
    """
    # 카드 목록 문자열 만들기
    card_lines = "\n".join(
        f"- {c['name']}: {', '.join(c['keywords'])}"
        for c in cards
    )
    user_prompt = (
        f"{spread_type}장 스프레드로 뽑힌 카드 목록:\n"
        f"{card_lines}\n\n"
        "각 카드의 의미와 전체 리딩을 한국어로 간결히 설명해주세요."
    )

    # 동기 create 호출 (await 제거)
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 전문 타로 리더입니다."},
            {"role": "user",   "content": user_prompt},
        ],
        max_tokens=500
    )

    return resp.choices[0].message.content.strip()