import vertexai
from vertexai.generative_models import GenerativeModel, Part
import io
import os
from PIL import Image
from google.oauth2 import service_account
from google.cloud import aiplatform
from vertexai.generative_models import Part
import time

# 1) Vertex AI 프로젝트 초기화
# YOUR_PROJECT_ID와 YOUR_LOCATION을 실제 값으로 변경하세요.
# 예시: vertexai.init(project="my-gcp-project", location="us-central1")
vertexai.init(project="spiritual-clock-459108-i2", location="us-central1")


def generate_vertex_image(input_image_path: str, prompt_text: str, output_image_path: str = None) -> bytes:
    # Imagen 3.0 Edit 모델 로드
    model = GenerativeModel("imagen-3.0-capability-001")

    # 원본 이미지 로드
    try:
        with open(input_image_path, "rb") as f:
            input_image_bytes = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_image_path}")

    # 이미지 데이터를 Vertex AI의 Part 객체로 변환
    input_image_part = Part.from_data(data=input_image_bytes, mime_type="image/jpeg")

    # 프롬프트 구성 (이미지 + 텍스트)
    prompt = [input_image_part, prompt_text]

    # 모델로부터 이미지 생성 요청
    image_response = model.generate_content(prompt)

    # 응답 처리
    if image_response.images:
        output_image_bytes = image_response.images[0]._image_bytes

        # output_image_path가 지정된 경우 파일로 저장
        if output_image_path:
            with open(output_image_path, "wb") as f:
                f.write(output_image_bytes)

        return output_image_bytes

    else:
        error_message = "이미지 생성 실패: 이미지가 반환되지 않았습니다."
        if image_response.candidates:
            reasons = [c.finish_reason for c in image_response.candidates if c.finish_reason]
            error_message += f" 이유: {', '.join(reasons)}"
        raise ValueError(error_message)

if __name__ == "__main__":
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    print(">> ADC 경로:", creds_path)
    print(">> 존재 여부:", os.path.exists(creds_path or ""))

    INPUT_IMAGE_PATH = r"D:\python_workspace\FastAPI\app\services\atelier\10674150-road-in-the-forest-in-autumn.jpg"
    OUTPUT_IMAGE_PATH = "edited_image_imagen_3_0.png"
    PROMPT_TEXT = "Apply a late autumn cyberpunk style. Make the leaves glow neon colors and add futuristic elements."

    print("🎨 Imagen 3.0 모델로 이미지 변환 요청 중...")

    try:
        generate_vertex_image(INPUT_IMAGE_PATH, PROMPT_TEXT, OUTPUT_IMAGE_PATH)
        print(f"✅ 이미지 생성 완료: '{OUTPUT_IMAGE_PATH}'")
        print("⏰ 다음 요청까지 5초 대기 중...")
        time.sleep(5)
    except Exception as e:
        print(f"❌ 이미지 생성 중 오류가 발생했습니다: {e}")