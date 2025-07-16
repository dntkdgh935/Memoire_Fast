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
    content: str
    title: str
    option: str
    inputText: str
    style: str
    memoryType: str
    collectionId: int
    memoryOrder: int
    memoryId: int
    userId: str
    saveToMemory: bool

class Config:
    allow_population_by_field_name = True

class TextResultDto(BaseModel):
    title: str
    content: str
    style: str
    memoryType: str
    collectionId: int
    memoryOrder: int

class ImageGenerationRequest(BaseModel):
    prompt: str
    style: str
    title: Optional[str]
    content: Optional[str] = None  # ✅ null 허용!
    collectionId: int
    saveToMemory: bool
    userId: str
    memoryType: str
    memoryOrder: int

# 이미지 생성 응답
class ImageResultDto(BaseModel):
    imageUrl: str
    filename: str
    filepath: str
    title: str
    prompt: str
    style: str
    memoryType: str
    collectionId: int
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