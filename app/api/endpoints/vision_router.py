from fastapi import APIRouter, UploadFile, File, Form
from app.services.atelier.visionapi_service import analyze_image

router = APIRouter()

@router.post("/analyze-image")
async def analyze_image_endpoint(image_url: str = Form(...)):
    description = analyze_image(image_url)
    return {"description": description}