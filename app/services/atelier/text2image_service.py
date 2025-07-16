import os
import uuid
import requests
from openai import OpenAI
from app.schemas.atelier_schema import ImageGenerationRequest, ImageResultDto
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📁 이미지 저장 경로 설정
UPLOAD_DIR = "static/images"  # 실제 서버 경로
PUBLIC_URL_PREFIX = "/images"  # 브라우저에서 접근할 URL 경로

# 🧠 이미지 다운로드 및 저장 함수
def save_image_from_url(image_url: str) -> tuple[str, str, str]:
    response = requests.get(image_url)
    response.raise_for_status()

    filename = f"{uuid.uuid4().hex}.jpg"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # 디렉토리 없으면 생성
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 이미지 저장
    with open(file_path, "wb") as f:
        f.write(response.content)

    return image_url, filename, f"{PUBLIC_URL_PREFIX}/{filename}"

# ✅ DALL·E API 호출 및 이미지 저장
def generate_image_from_dalle(request: ImageGenerationRequest) -> ImageResultDto:
    prompt_parts = [request.prompt]
    if request.style:
        prompt_parts.append(f"스타일: {request.style}")
    if hasattr(request, "option") and request.option:
        prompt_parts.append(f"추가 요청: {request.option}")

    final_prompt = "\n".join(prompt_parts)

    # DALL·E 호출
    response = client.images.generate(
        model="dall-e-3",
        prompt=final_prompt,
        size="1024x1024",
        n=1
    )

    image_url = response.data[0].url

    # ✅ 서버에 이미지 저장
    _, filename, filepath = save_image_from_url(image_url)

    # 🎁 최종 결과 반환
    return ImageResultDto(
        imageUrl=image_url,
        prompt=request.prompt,
        title=request.title,
        filename=filename,
        filepath=filepath,
        style=request.style,
        memoryType=request.memoryType,
        collectionId=request.collectionId,
        memoryOrder=request.memoryOrder
    )