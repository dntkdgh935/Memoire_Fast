from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.atelier.visionapi_service import analyze_image

router = APIRouter()

@router.post("/analyze-image", summary="이미지 설명 생성")
async def analyze_image_endpoint(
    image_url: str = Form(..., description="로컬 경로 또는 HTTP/HTTPS URL")
):
    try:
        description = analyze_image(image_url)
        return {"description": description}
    except ValueError as e:
        # 다운로드나 파일 처리 오류
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # GPT 호출 등 내부 오류
        raise HTTPException(status_code=500, detail=str(e))