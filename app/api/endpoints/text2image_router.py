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
            "size": {"type": "string", "enum": ["256x256","512x512","1024x1024"], "default": "1024x1024"},
            "n": {"type": "integer", "default": 1, "description": "생성할 이미지 개수"}
        },
        "required": ["prompt"]
    }
}]

# 2) 범용(일러스트 등) 시스템 템플릿
GENERAL_TEMPLATE = """
You are a world-class DALL·E 3 prompt engineer.
Given STYLE_DESC, SCENE, and ADDITIONAL NOTES, produce one ultra-detailed English prompt
that satisfies ALL of these:
 1) exact STYLE_DESC
 2) background setting (interior/exterior, location, time, weather)
 3) composition (camera angle, framing, perspective)
 4) lens/shot type (e.g., 50mm f/1.2, wide-angle)
 5) exposure settings (aperture, ISO, shutter speed)
 6) lighting & mood (cinematic, warm/cool, natural)
 7) textures & materials (watercolor textures, cel-shaded line art, fabric weave)
 8) color palette & grading (pastel, vibrant, film grain)
 9) emotional tone (heartwarming, dramatic, serene)
10) high-detail hints (\"ultra-detailed\", \"8K\")

After writing the prompt, self-review against these ten criteria and fill any gaps.
Return ONLY the final prompt.
"""

# 3) 포토리얼 특화 시스템 템플릿 (negative instructions 포함)
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
    style_resp = await gpt.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content":
                "You are a style translator. "
                "Given a style keyword, output a concise English style descriptor."},
            {"role": "user", "content": f"Style: {request.style}"}
        ],
        temperature=0.7,
        max_tokens=60,
    )
    style_desc = style_resp.choices[0].message.content.strip()

    # 2) 어떤 템플릿 사용할지 결정
    if is_photoreal_style(style_desc):
        system_template = PHOTO_TEMPLATE
    else:
        system_template = GENERAL_TEMPLATE

    # 3) GPT에 최종 프롬프트 생성 요청 (Function Calling)
    user_msg = (
        f"STYLE_DESC: {style_desc}\n"
        f"SCENE: {request.content}\n"
        f"ADDITIONAL NOTES: {request.otherRequest or 'none'}"
    )
    chat_resp = await gpt.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_template},
            {"role": "user",   "content": user_msg}
        ],
        functions=FUNCTIONS,
        function_call={"name": "generate_image_dall_e"},
        temperature=0.3,
        max_tokens=400
    )

    fn_call = chat_resp.choices[0].message.function_call
    args    = fn_call.arguments or {}
    prompt  = args.get("prompt")
    size    = args.get("size", "1024x1024")
    n       = args.get("n", 1)

    if not prompt:
        raise HTTPException(status_code=500, detail="Failed to generate prompt")

    # 4) negative instructions: photoreal 분기일 때 추가
    if is_photoreal_style(style_desc):
        prompt = prompt.strip()
        prompt += " —no illustration, no watercolor, no cartoon, no sketch, no line art"

    # 5) DALL·E 3에 이미지 생성 요청
    dalle_resp = await gpt.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size=size,
        n=n
    )

    image_url = dalle_resp.data[0].url
    return ImageResultDto(imageUrl=image_url)