# app/services/atelier/vertex_service.py
import os, io, uuid, requests
from diffusers import StableDiffusionImg2ImgPipeline
import torch
from PIL import Image

# 1) 파이프라인을 모듈 로드 시 한 번만 초기화
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DTYPE  = torch.float16 if DEVICE=="cuda" else torch.float32

PIPE = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=DTYPE
).to(DEVICE)
PIPE.enable_attention_slicing()

# 2) 실제 이미지 생성 함수
async def generate_vertex_image(prompt: str, image_url: str) -> str:
    # 2-1) 원본 이미지 다운로드
    resp = requests.get(image_url, timeout=10)
    resp.raise_for_status()
    init_image = Image.open(io.BytesIO(resp.content)).convert("RGB")
    init_image = init_image.resize((512, 512))  # 모델 안정화를 위해 리사이즈

    # 2-2) img2img 실행
    result = PIPE(
        prompt=prompt,
        image=init_image,
        strength=0.3,            # 0.2~0.5 사이로
        guidance_scale=7.5,
        num_inference_steps=30
    )
    output_img = result.images[0]

    # 2-3) 저장 (static 디렉터리에 UUID 파일명)
    out_fname = f"vertex_{uuid.uuid4().hex}.png"
    out_path  = os.path.join("static", out_fname)
    output_img.save(out_path)

    # 2-4) 최종 접근 가능 URL 반환
    #    예: https://your-domain.com/static/vertex_abc123.png
    base_url = os.getenv("STATIC_BASE_URL", "http://localhost:8000/static")
    return f"{base_url}/{out_fname}"
