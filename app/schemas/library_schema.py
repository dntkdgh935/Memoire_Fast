# app/schemas/recommend_schema.py

from pydantic import BaseModel

class RecommendRequest(BaseModel):
    userid: str

class RecommendedItem(BaseModel):
    item_id: int
    score: float
