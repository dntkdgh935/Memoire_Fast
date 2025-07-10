from fastapi import APIRouter
from app.schemas.atelier_schema import TextGenerationRequest, TextResultDto
from app.services.atelier import textgen_service

router = APIRouter()

@router.post("/generate-text", response_model=TextResultDto)
def generate_text(request: TextGenerationRequest):
    try:
        return textgen_service.generate_text_from_gpt(request)
    except Exception as e:
        return {"error": str(e)}
