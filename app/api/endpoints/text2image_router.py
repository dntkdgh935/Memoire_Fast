from fastapi import APIRouter, Response
from app.schemas.atelier_schema import ImageGenerationRequest, ImageResultDto
from app.services.atelier.text2image_service import generate_image_from_dalle

router = APIRouter()

@router.options("/generate-image")
async def preflight_handler():
    return Response(status_code=200)

@router.post("/generate-image", response_model=ImageResultDto)
async def generate_image(request: ImageGenerationRequest):
    print("🔥 generate_image 호출됨")
    print(f"📥 content 필드 값: {request.content} ({type(request.content)})")
    return generate_image_from_dalle(request)

print("✅ text2image_router.py 라우터 등록 상태 확인:")
for route in router.routes:
    print(f"➡️ method={route.methods}, path={route.path}")