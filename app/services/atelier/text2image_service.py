import os
from openai import OpenAI

from app.core.config import settings
from app.schemas.atelier_schema import ImageGenerationRequest, ImageResultDto

# OpenAI API 클라이언트
client = OpenAI(api_key=settings.openai_api_key)

def generate_image(request: ImageGenerationRequest) -> ImageResultDto:
    try:
        # 프롬프트에 스타일 적용
        styled_prompt = f"{request.style} 스타일로 이미지 생성: {request.prompt}"

        # DALL·E 3 이미지 생성
        response = client.images.generate(
            model="dall-e-3",
            prompt=styled_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        image_url = response.data[0].url

        return ImageResultDto(
            imageUrl=image_url,
            style=request.style,
            memoryType=request.memoryType,
            collectionId=request.collectionId,
            memoryOrder=request.memoryOrder
        )

    except Exception as e:
        raise RuntimeError(f"이미지 생성 오류: {str(e)}")