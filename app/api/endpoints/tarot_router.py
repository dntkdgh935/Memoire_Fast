from fastapi import APIRouter
import random
from app.data.tarot_deck import tarot_deck  # ✅ 카드 정보 리스트 (이미 image 경로 포함됨)
from app.services.tarot.tarot_service import generate_reading
from fastapi.concurrency import run_in_threadpool

router = APIRouter(prefix="/tarot", tags=["tarot"])

# ✅ 카드 n장 뽑기
@router.get("/draw/{count}")
async def draw_cards(count: int):
    if count < 1 or count > len(tarot_deck):
        return {"error": "Invalid count"}
    drawn = random.sample(tarot_deck, count)
    return {"cards": drawn}

# ✅ 카드 n장 + 해석까지 요청 (POST)
@router.post("/read/{count}")
async def read_tarot(count: int):
    if count < 1 or count > len(tarot_deck):
        return {"error": "Invalid count"}
    drawn = random.sample(tarot_deck, count)
    reading = await run_in_threadpool(generate_reading, str(count), drawn)
    return {"cards": drawn, "reading": reading}

# ✅ 123전체 카드 목록 반환 (프론트에서 목록용으로 사용 가능)
@router.get("/cards")
async def get_all_cards():
    return {"cards": tarot_deck}