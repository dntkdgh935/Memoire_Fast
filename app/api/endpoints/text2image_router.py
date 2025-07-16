# app/routers/text2image_router.py

from fastapi import APIRouter, Response
from openai import OpenAI
from app.core.config import settings
from app.schemas.atelier_schema import ImageGenerationRequest, ImageResultDto
from app.services.atelier.text2image_service import generate_image_from_dalle

router = APIRouter()
gpt_client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def expand_prompt(style: str, scene: str, other: str) -> str:
    """
    1) 한글 입력은 영어로 번역
    2) STYLE 단어는 그대로 살리면서
    3) composition, lighting, textures, colors, resolution 디테일을 붙임
    4) temperature 낮춰서 일관성 확보
    """
    system = """
You are an expert prompt engineer. When given STYLE, SCENE, and ADDITIONAL NOTES in any language,
you must:
  1) Translate STYLE and SCENE to English if needed.
  2) Use exactly the translated STYLE text in your prompt.
  3) Describe composition (camera angle, framing).
  4) Specify lighting and mood.
  5) Call out textures and colors.
  6) Add a resolution hint (e.g., '8K', 'ultra-detailed').
Output only the final prompt text—no explanations.
"""
    user = (
        f"STYLE: {style}\n"
        f"SCENE: {scene}\n"
        f"ADDITIONAL NOTES: {other or 'none'}\n\n"
        "Please generate a single, richly detailed DALL·E 3 prompt:"
    )

    resp = await gpt_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ],
        temperature=0.3,     # 낮은 온도로 일관성 높이기
        max_tokens=250,
    )
    return resp.choices[0].message.content.strip()


@router.options("/generate-image")
async def preflight_handler():
    return Response(status_code=200)


@router.post("/generate-image", response_model=ImageResultDto)
async def generate_image(request: ImageGenerationRequest):
    # 1) 입력을 GPT로 한 번더 “영어 번역 + 디테일 확장”
    expanded = await expand_prompt(
        style=request.style,
        scene=request.content,
        other=request.otherRequest
    )

    # 2) 확장된 영어 프롬프트를 content에 덮어쓰기
    request.content = expanded

    # 3) 기존 DALL·E 호출 로직 그대로 사용
    return generate_image_from_dalle(request)


print("✅ text2image_router.py 라우터 등록 상태 확인:")
for route in router.routes:
    print(f"➡️ method={route.methods}, path={route.path}")