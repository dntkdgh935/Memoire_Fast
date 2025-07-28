from fastapi import APIRouter
import random
from app.data.tarot_deck import tarot_deck
from app.services.tarot.tarot_service import generate_reading  # 수정된 import 경로
from fastapi.concurrency import run_in_threadpool
from app.data.tarot_deck import TAROT_CARDS

router = APIRouter(prefix="/tarot", tags=["tarot"])

@router.get("/draw/{count}")
async def draw_cards(count: int):
    if count < 1 or count > len(tarot_deck):
        return {"error": "Invalid count"}
    drawn = random.sample(tarot_deck, count)
    return {"cards": drawn}

@router.post("/read/{count}")
async def read_tarot(count: int):
    drawn = random.sample(tarot_deck, count)
    # 동기 함수를 스레드 풀에서 실행
    reading = await run_in_threadpool(generate_reading, str(count), drawn)
    return {"cards": drawn, "reading": reading}

@router.get("/api/tarot/cards")
async def get_all_tarot_cards():
    return TAROT_CARDS