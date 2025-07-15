from fastapi import APIRouter
from app.schemas.atelier_schema import TextGenerationRequest, TextResultDto
from app.services.atelier.textgen_service import generate_text_from_gpt
from fastapi import APIRouter, Response

router = APIRouter()

@router.options("/generate-text")
async def preflight_handler():
    return Response(status_code=200)

@router.post("/generate-text", response_model=TextResultDto)
async def generate_text(request: TextGenerationRequest):
    print("🔥 FastAPI 요청 도착")  # 반드시 터미널에 출력돼야 함
    return generate_text_from_gpt(request)