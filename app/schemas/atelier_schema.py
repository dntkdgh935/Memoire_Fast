from pydantic import BaseModel, HttpUrl
from typing import Optional, Literal


class LipSyncRequest(BaseModel):
    image_url: HttpUrl
    audio_url: HttpUrl

class LipSyncResponse(BaseModel):
    video_url: str

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
    otherRequest: Optional[str] = None

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


class RunwayGenerationRequest(BaseModel):
    image_url: str
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
    video_url: str


class VertexGenerationRequest(BaseModel):
    prompt: str
    image_url: str

class VertexGenerationResponse(BaseModel):
    generated_image_url: str

# sync 모델 사용 안할 경우 영상 생성 Request
class VideoPipelineRequest(BaseModel):
    image_url: str
    prompt: Optional[str] = None
    tts_url: Optional[str] = None

class VideoPipelineResponse(BaseModel):
    video_url: str

class MediaPipelineRequest(BaseModel):
    raw_video_url: str
    image_url: str
    tts_url: Optional[str] = None
    duration: int = 15
    num_steps: int = 25

class MediaPipelineResponse(BaseModel):
    final_video_url: str

# tts 스크립트 호출
class TtsConfigRequest(BaseModel):
    script: str
    voiceGender: Literal["female", "male"]

class TtsConfigResponse(BaseModel):
    voice_id: str
    model_id: str
    stability: float
    similarity_boost: float

# elevenlabs 부분
class TtsGenerateRequest(BaseModel):
    speech: str
    voice_id: str
    model_id: str
    stability: float
    similarity_boost: float

class TtsGenerateResponse(BaseModel):
    audio_url: str


# 사용 안함 ---------------------------------------------------------
class StableGenerationRequest(BaseModel):
    prompt: str
    duration: int
    numSteps: int

class StableGenerationResponse(BaseModel):
    generated_natural_url: str