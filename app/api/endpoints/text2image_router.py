# app/routers/text2image_router.py

from fastapi import APIRouter, Response, HTTPException
from openai import OpenAI
from app.core.config import settings
from app.schemas.atelier_schema import ImageGenerationRequest, ImageResultDto

router = APIRouter()
gpt = OpenAI(api_key=settings.OPENAI_API_KEY)

# 1) DALL·E 호출 함수 스펙 (Function Calling)
FUNCTIONS = [{
    "name": "generate_image_dall_e",
    "description": "DALL·E 3를 사용해 이미지를 생성합니다.",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "최종 프롬프트 문장"},
            "size": {"type": "string", "enum": ["256x256", "512x512", "1024x1024"], "default": "1024x1024"},
            "n": {"type": "integer", "default": 1, "description": "생성할 이미지 개수"}
        },
        "required": ["prompt"]
    }
}]

# 2) 스타일 템플릿
GENERAL_TEMPLATE = """
You are a world-class visual prompt engineer for DALL·E 3.

Your MOST IMPORTANT TASK is to generate a highly detailed English prompt that transforms text into an image.

Follow these rules strictly:
1. The visual STYLE must match STYLE_DESC (e.g., cartoon, watercolor, oil painting, pixel art, poster).
2. Include key visual elements from SCENE (location, setting, characters, atmosphere).
3. Integrate ADDITIONAL NOTES naturally as visual ideas.
4. Describe composition: camera angle, perspective, subject placement.
5. Describe lighting: ambient, directional, natural, dramatic.
6. Describe texture, color grading, and mood in visual terms.
7. Add artistic modifiers: ultra-detailed, trending on ArtStation, 8K.

Avoid vagueness. Be precise and visually rich.

Respond with ONLY the final English prompt.
"""

PHOTO_TEMPLATE = """
You are a world-class photorealistic prompt engineer.
Every prompt MUST include:
 - Camera specs: brand, model, lens focal length, aperture, ISO, shutter speed
 - Lighting: golden-hour or natural daylight with soft fill
 - Textures: natural skin pores, fabric weave, wood grain
 - Composition: angle, framing, depth of field
 - Color grading: filmic, warm tones, subtle film grain
 - Negative instructions: —no illustration, no watercolor, no cartoon, no sketch, no line art
 - High-detail hints: ultra-detailed, 8K, photorealistic

Self-review against these points and return ONLY the final prompt.
"""

def is_photoreal_style(text: str) -> bool:
    txt = text.lower()
    return any(k in txt for k in ["photo", "photoreal", "실사", "사진", "camera", "canon", "nikon", "mirrorless"])

@router.options("/generate-image")
async def preflight_handler():
    return Response(status_code=200)

@router.post("/generate-image", response_model=ImageResultDto)
async def generate_image(request: ImageGenerationRequest):
    # 1) 스타일 → 영어 디스크립터 변환
    style_resp = gpt.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are a visual style translator. "
                "Given a short Korean style description (e.g. '카툰스타일'), return a detailed English phrase that describes its visual elements. "
                "Output should describe texture, composition, and color tone in 1~2 sentences."
             },
            {"role": "user", "content": f"Style: {request.style}"}
        ],
        temperature=0.7,
        max_tokens=60,
    )
    style_desc = style_resp.choices[0].message.content.strip()

    # 2) 템플릿 결정
    system_template = PHOTO_TEMPLATE if is_photoreal_style(style_desc) else GENERAL_TEMPLATE

    # 3) 프롬프트 생성
    user_msg = (
        f"[STYLE_DESC]\n{style_desc}\n\n"
        f"[SCENE]\n{request.content.strip()}\n\n"
        f"[ADDITIONAL NOTES]\n{request.otherRequest.strip() if request.otherRequest else 'none'}"
    )

    chat_resp = gpt.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_template},
            {"role": "user", "content": user_msg}
        ],
        functions=FUNCTIONS,
        function_call={"name": "generate_image_dall_e"},
        temperature=0.3,
        max_tokens=400
    )

    fn_call = chat_resp.choices[0].message.function_call
    arguments = fn_call.arguments
    if isinstance(arguments, str):
        import json
        arguments = json.loads(arguments)

    prompt = arguments.get("prompt")
    size = arguments.get("size", "1024x1024")
    n = arguments.get("n", 1)

    if not prompt:
        raise HTTPException(status_code=500, detail="프롬프트 생성 실패")

    if is_photoreal_style(style_desc):
        prompt += " —no illustration, no watercolor, no cartoon, no sketch, no line art"

    # 4) DALL·E 이미지 생성
    dalle_resp = gpt.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        n=n
    )
    image_url = dalle_resp.data[0].url

    # 5) 전체 DTO로 응답 반환
    return ImageResultDto(
        imageUrl=image_url,
        filename="generated_image.png",
        filepath="",  # 저장 안 한 경우 공백
        title=request.title,
        prompt=prompt,
        style=request.style,
        memoryType=request.memoryType,
        collectionId=request.collectionId,
        memoryOrder=request.memoryOrder
    )