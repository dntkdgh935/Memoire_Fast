import os
from openai import OpenAI
from app.schemas.atelier_schema import ImageGenerationRequest, ImageResultDto
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_image_from_dalle(request: ImageGenerationRequest) -> ImageResultDto:
    prompt_parts = [request.prompt]
    if request.style:
        prompt_parts.append(f"스타일: {request.style}")
    if hasattr(request, "option") and request.option:
        prompt_parts.append(f"추가 요청: {request.option}")

    final_prompt = "\n".join(prompt_parts)

    response = client.images.generate(
        model="dall-e-3",
        prompt=final_prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )

    image_url = response.data[0].url

    return ImageResultDto(
        imageUrl=image_url,
        prompt=request.prompt,
        title=request.title,
        filename=None,
        filepath=None,
        style=request.style,
        memoryType=request.memoryType,
        collectionId=request.collectionId,
        memoryOrder=request.memoryOrder
    )