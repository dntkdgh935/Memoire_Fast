# app/schemas/library_schema.py

# 너무 단순해서 아마 삭제할 것
from pydantic import BaseModel

class KeywordSearchRequest(BaseModel):
    query: str
    userid: str
