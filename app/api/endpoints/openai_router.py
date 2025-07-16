from fastapi import APIRouter
from starlette.responses import JSONResponse
from app.schemas.atelier_schema import OpenaiGenerationRequest, OpenaiGenerationResponse
from app.services.atelier.prompt_service import PromptRefiner
import json

router = APIRouter()

@router.post("/generate", response_model=OpenaiGenerationResponse)
async def openai_text_endpoint(request: OpenaiGenerationRequest):
    req_dict = request.dict()
    raw_json = json.dumps(req_dict, ensure_ascii=False)

    refiner = PromptRefiner()
    prompts = refiner.execute(raw_json)

    return JSONResponse(content=prompts)
