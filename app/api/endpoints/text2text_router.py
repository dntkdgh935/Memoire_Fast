from fastapi import APIRouter
from app.schemas.atelier_schema import TextGenerationRequest, TextResultDto
from app.services.atelier.textgen_service import generate_text_from_gpt
from fastapi import APIRouter, Response
from fastapi import Request

router = APIRouter()

@router.options("/generate-text")
async def preflight_handler():
    return Response(status_code=200)

@router.post("/generate-text", response_model=TextResultDto)
async def generate_text(request: TextGenerationRequest):
    print("🔥 FastAPI 요청 도착")
    print("📦 실제로 받은 JSON:", request)

    result = generate_text_from_gpt(request)
    return result