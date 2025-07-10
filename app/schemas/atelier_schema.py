from pydantic import BaseModel, HttpUrl


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
    prompt: str
    style: str  # 예: dreamy, surreal, dark 등
    memoryType: str
    collectionId: str
    memoryOrder: int
    saveToMemory: bool

# 이미지 생성 응답
class ImageResultDto(BaseModel):
    imageUrl: str
    style: str
    memoryType: str
    collectionId: str
    memoryOrder: int
