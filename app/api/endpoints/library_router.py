# app/api/endpoints/library_router.py

from fastapi import APIRouter, HTTPException
from app.schemas.library_schema import RecommendRequest, RecommendedItem
from app.services.library.recommend_service import get_liked_items_from_db, recommend_items

router = APIRouter(prefix="/library", tags=["Library"])


@router.post("/recommend", response_model=list[RecommendedItem])
def recommend_endpoint(request: RecommendRequest):
    user_id = request.userid  # 유저 ID를 받음

    try:
        # 1. 유저가 좋아요한 아이템 ID 조회 (DB)
        liked_items = get_liked_items_from_db(user_id)

        # 2. 추천 아이템 계산
        recommendations = recommend_items(liked_items)

        return recommendations  # 추천 결과 반환
    except Exception as e:
        raise HTTPException(status_code=500, detail="추천 시스템 오류")
