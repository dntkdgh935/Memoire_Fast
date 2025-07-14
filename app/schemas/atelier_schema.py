from pydantic import BaseModel, HttpUrl
from typing import Optional


class ComposeRequest(BaseModel):
    image_url: HttpUrl
    background_prompt: str
    music_prompt: str
    tts_text: str

class ComposeResponse(BaseModel):
    video_path: str

class TextGenerationRequest(BaseModel):
    inputText: str
    style: str
    memoryType: str
    collectionId: str
    memoryOrder: int
    saveToMemory: bool

class TextResultDto(BaseModel):
    title: str
    content: str
    style: str
    memoryType: str
    collectionId: str
    memoryOrder: int

# 이미지 생성 요청
class ImageGenerationRequest(BaseModel):
    prompt: str                 # 기타 요청 (사용자 입력)
    style: str                 # 스타일 (사용자 입력)
    title: str                 # 저장할 제목
    originalText: str          # 저장할 설명 또는 원문 텍스트
    collectionId: int          # 소속 컬렉션 ID
    saveToMemory: bool = True  # 저장 여부
    userId: Optional[str]      # 사용자 ID
    memoryType: str = "image"  # 고정값
    memoryOrder: int = 0       # 정렬 순서 (기본 0)

# 이미지 생성 응답
class ImageResultDto(BaseModel):
    imageUrl: str
    style: str
    memoryType: str
    collectionId: str
    memoryOrder: int
