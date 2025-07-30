from pydantic import BaseModel
from typing import List

class TarotCard(BaseModel):
    name: str
    image: str
    meaning: str

class TarotReadRequest(BaseModel):
    cards: List[TarotCard]