# app/services/atelier/gpt_image_service.py

import openai
import base64
from pathlib import Path
from PIL import Image
from app.core.config import settings
from app.services.atelier.prompt_service import PromptRefiner

_refiner = PromptRefiner()

openai.api_key = settings.OPENAI_API_KEY

def edit_with_gpt_image_base64(
    image_path: str,
    style_prompt: str,
    n: int = 1,
    size: str = "1024x1024",
    model: str = "gpt-image-1",
) -> list[str]:
    # 원본 + 전체 흰색 마스크 준비
    img = Image.open(image_path).convert("RGBA")
    mask = Image.new("RGBA", img.size, (255, 255, 255, 255))
    tmp_img, tmp_mask = Path("tmp_img.png"), Path("tmp_mask.png")
    img.save(tmp_img); mask.save(tmp_mask)

    refined = _refiner.refine_image_prompt(style_prompt)

    # edit 호출 (response_format 없이)
    with tmp_img.open("rb") as i, tmp_mask.open("rb") as m:
        resp = openai.images.edit(
            model=model,
            image=i,
            mask=m,
            prompt=refined,
            n=n,
            size=size
        )

    out_urls = []
    for idx, data in enumerate(resp.data):
        b64 = data.b64_json
        img_bytes = base64.b64decode(b64)
        out = Path("out")/f"styled_{idx}.png"
        out.parent.mkdir(exist_ok=True)
        out.write_bytes(img_bytes)
        out_urls.append(str(out.resolve()))
    return out_urls

