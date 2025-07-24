# app/services/atelier/visionapi_service.py
import tempfile, shutil, requests, base64
from pathlib import Path
from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def analyze_image(image_path_or_url: str) -> str:
    # 1) URL vs 로컬 처리하여 image_file(Path) 획득 (생략)
    tmp_dir = None
    if image_path_or_url.startswith(("http://", "https://")):
        tmp_dir    = Path(tempfile.mkdtemp())
        local_file = tmp_dir / Path(image_path_or_url).name
        resp       = requests.get(image_path_or_url, stream=True)
        resp.raise_for_status()
        local_file.write_bytes(resp.content)
        image_file = local_file
    else:
        image_file = Path(image_path_or_url)
        if not image_file.is_file():
            raise ValueError(f"로컬 이미지 파일이 없습니다: {image_path_or_url}")

    try:
        # 2) Data URI 생성
        data = image_file.read_bytes()
        ext  = image_file.suffix.lstrip(".")
        b64  = base64.b64encode(data).decode()
        data_uri = f"data:image/{ext};base64,{b64}"

        # 3) GPT‑4o 멀티모달 호출 (content는 문자열)
        user_prompt = (
            "다음 이미지를 상세하게 묘사해 주세요:\n"
            f"{data_uri}"
        )
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role":"system", "content":"You are an expert at vividly describing images."},
                {"role":"user",   "content": user_prompt},
            ],
            max_tokens=300,
        )
        return resp.choices[0].message.content

    finally:
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)
