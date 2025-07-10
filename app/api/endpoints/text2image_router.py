# app/api/endpoints/text2image_router.py
from fastapi import APIRouter
from app.schemas.atelier_schema import ImageGenerationRequest, ImageResultDto
from app.services.atelier import text2image_service

print("✅ [Router 파일 로드 확인] text2image_router.py 실행됨")

router = APIRouter(tags=["AI"])

@router.post("/generate-image", response_model=ImageResultDto)
def generate_image(request: ImageGenerationRequest):
    print("✅ [API 호출 확인] generate_image 호출됨")
    return text2image_service.generate_image(request)