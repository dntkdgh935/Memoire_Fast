from io import BytesIO
import uuid
import openai
import base64
import requests
from pathlib import Path
from PIL import Image
from app.core.config import settings
from app.services.atelier.prompt_service import PromptRefiner

_refiner = PromptRefiner()

openai.api_key = settings.OPENAI_API_KEY
MAX_SIZE_BYTES = 200 * 1024 * 1024

def edit_with_gpt_image_base64(
    image_path: str,
    style_prompt: str,
    n: int = 1,
    size: str = "1024x1024",
    model: str = "gpt-image-1"
) -> list[str]:
    print(f"[im2im] called with image_path={image_path!r}, style_prompt={style_prompt!r}")

    if image_path.startswith("http://") or image_path.startswith("https://"):
        print("[im2im] fetching image via HTTP")
        resp = requests.get(image_path)
        print(f"[im2im] HTTP status: {resp.status_code}")
        resp.raise_for_status()
        img_bytes = resp.content
        img = Image.open(BytesIO(img_bytes)).convert("RGBA")
    else:
        print("[im2im] opening local image file")
        img = Image.open(image_path).convert("RGBA")

    print(f"[im2im] image size: {img.size}")

    mask = Image.new("RGBA", img.size, (255, 255, 255, 255))
    tmp_img, tmp_mask = Path("tmp_img.png"), Path("tmp_mask.png")
    img.save(tmp_img); mask.save(tmp_mask)
    print(f"[im2im] saved tmp_img={tmp_img} tmp_mask={tmp_mask}")


    refined = _refiner.refine_image_prompt(style_prompt)
    print(f"[im2im] refined prompt: {refined!r}")


    with tmp_img.open("rb") as i, tmp_mask.open("rb") as m:
        resp = openai.images.edit(
            model=model,
            image=i,
            mask=m,
            prompt=refined,
            n=n,
            size=size
        )
    print(f"[im2im] OpenAI images.edit returned {len(resp.data)} items")

    output_dir = Path("C:/upload_files/memory_img")
    output_dir.mkdir(parents=True, exist_ok=True)

    out_urls = []
    for idx, data in enumerate(resp.data):
        b64 = data.b64_json
        img_bytes = base64.b64decode(b64)
        out = f"{uuid.uuid4().hex}.png"
        local_path = output_dir / out
        local_path.write_bytes(img_bytes)

        out_urls.append(f"/upload_files/memory_img/{out}")
        print(f"[im2im] wrote output[{idx}]: {local_path}")


    return out_urls

