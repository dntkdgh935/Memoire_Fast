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

class ElevenlabsGenerationRequest(BaseModel):
    prompt: str
    text: str

class ElevenlabsGenerationResponse(BaseModel):
    audio_url: str


class RunwayGenerationRequest(BaseModel):
    image_url: str
    prompt: str
    tts_url: str

class RunwayGenerationResponse(BaseModel):
    video_url: str


class OpenaiGenerationRequest(BaseModel):
    prompt: str

class OpenaiGenerationResponse(BaseModel):
    generated_text: str


class FfmpegGenerationRequest(BaseModel):
    video_url: str
    tts_url: str

class FfmpegGenerationResponse(BaseModel):
    processed_video_url: str


class VertexGenerationRequest(BaseModel):
    prompt: str
    image_url: str

class VertexGenerationResponse(BaseModel):
    generated_image_url: str