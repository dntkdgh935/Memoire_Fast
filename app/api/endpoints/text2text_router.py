from fastapi import APIRouter, HTTPException
from app.schemas.atelier_schema import TextGenerationRequest, TextResultDto
from app.services.atelier import textgen_service


router = APIRouter()

@router.post("/generate-text", response_model=TextResultDto)
def generate_text(request: TextGenerationRequest):
    print("🔥 GPT 요청 도착:", request.prompt)
    return textgen_service.generate_text_from_gpt(request)
