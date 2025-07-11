from fastapi import APIRouter
from app.schemas.atelier_schema import OpenaiGenerationRequest, OpenaiGenerationResponse
from app.services.atelier.textgen_service import generate_openai_text

router = APIRouter()

@router.post("/generate", response_model=OpenaiGenerationResponse)
async def openai_text_endpoint(request: OpenaiGenerationRequest):
    text = generate_openai_text(request.prompt)
    return OpenaiGenerationResponse(generated_text=text)
