from fastapi import APIRouter
from app.schemas.atelier_schema import VertexGenerationRequest, VertexGenerationResponse
from app.services.atelier.vertex_service import

router = APIRouter()

@router.post("/generate", response_model=VertexGenerationResponse)
async def vertex_endpoint(request: VertexGenerationRequest):
    generated_image_url = generate_vertex_image(request.prompt, request.image_url)
    return VertexGenerationResponse(generated_image_url=generated_image_url)
