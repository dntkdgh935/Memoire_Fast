from fastapi import APIRouter
import random
from app.data.tarot_deck import tarot_deck  # ✅ 카드 정보 리스트 (이미 image 경로 포함됨)
from app.services.tarot.tarot_service import generate_reading
from fastapi.concurrency import run_in_threadpool
from fastapi import Body
from typing import List, Dict
from app.schemas.tarot_schema import TarotReadRequest
import logging

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
async def read_tarot(count: int, request: TarotReadRequest = Body(...)):
    # 👇 여기에 추가
    logging.warning(f"들어온 카드 목록: {request.cards}")

    # 카드 개수 유효성 검사
    if count < 1 or count > len(request.cards):
        return {"error": "Invalid count"}

    # 리딩 처리
    reading = generate_reading(str(count), request.cards)
    return {"cards": request.cards, "reading": reading}

# ✅ 123전체 카드 목록 반환 (프론트에서 목록용으로 사용 가능)
@router.get("/cards")
async def get_all_cards():
    return {"cards": tarot_deck}