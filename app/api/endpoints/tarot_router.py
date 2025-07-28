from fastapi import APIRouter
import random
from app.data.tarot_deck import tarot_deck

from app.services.tarot.tarot_service import generate_reading
from fastapi.concurrency import run_in_threadpool
from app.data.tarot_deck import TAROT_CARDS

router = APIRouter(prefix="/tarot", tags=["tarot"])

# ✅ 카드 n장 뽑기
@router.get("/draw/{count}")
async def draw_cards(count: int):
    if count < 1 or count > len(tarot_deck):
        return {"error": "Invalid count"}

    drawn = random.sample(tarot_deck, count)

    # 카드에 이미지 경로 추가
    for i, card in enumerate(drawn):
        card["image"] = f"/cards/card_{i}.png"  # 이미지 경로 부여

    return {"cards": drawn}

# ✅ 카드 n장 + 해석까지 요청 (POST)
@router.post("/read/{count}")
async def read_tarot(count: int):
    if count < 1 or count > len(tarot_deck):
        return {"error": "Invalid count"}
    drawn = random.sample(tarot_deck, count)
    reading = await run_in_threadpool(generate_reading, str(count), drawn)
    return {"cards": drawn, "reading": reading}

# ✅ 전체 카드 목록 반환 (프론트에서 목록용으로 사용 가능)
@router.get("/cards")
async def get_all_tarot_cards():
    return {"cards": tarot_deck}
