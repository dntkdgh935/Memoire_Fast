from fastapi import APIRouter
from app.schemas.atelier_schema import VertexGenerationRequest, VertexGenerationResponse
from app.services.atelier.vertex_service import edit_with_gpt_image_base64
import logging as log

router = APIRouter()

@router.post("/generate", response_model=VertexGenerationResponse)
async def vertex_endpoint(request: VertexGenerationRequest):
    print("👉 im2im_generate called with:", request)
    url = await edit_with_gpt_image_base64(request.prompt, request.image_url)
    return VertexGenerationResponse(generated_image_url=url)
