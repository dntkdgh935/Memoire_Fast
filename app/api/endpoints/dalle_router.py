from fastapi import APIRouter, HTTPException
from app.schemas.atelier_schema import DallEGenerationRequest, DallEGenerationResponse
from app.services.atelier.dalle_service import edit_with_gpt_image_base64

router = APIRouter()

@router.post("/generate", response_model=DallEGenerationResponse)
def dalle_endpoint(request: DallEGenerationRequest):
    print("👉 im2im_generate called with:", request)
    try:
        out_urls = edit_with_gpt_image_base64(
            image_path=request.image_url,
            style_prompt=request.prompt,
        )
    except Exception as e:
        print("[im2im][ERROR]", e)
        raise HTTPException(status_code=500, detail=str(e))
    return DallEGenerationResponse(generated_image_url=out_urls[0])
