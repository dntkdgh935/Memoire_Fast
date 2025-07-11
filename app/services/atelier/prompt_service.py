import os
import sys
import json
from openai import OpenAI
from app.core.config import settings


class PromptRefiner:

    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def refine_all_prompts(self, inputs: dict[str, str]) -> dict[str, str]:
        system_prompt = (
            "You are an expert prompt-refiner. Given raw descriptions for:"
            "\n1) TTS generation"
            "\n2) Video with a person"
            "\n3) Video without a person"
            "\n4) Image generation"
            "\nTranslate and refine each description into high-quality English prompts optimized for its target API,"
            " and return a JSON with keys:\n"
            "- \"tts_prompt\": detailed, natural text for speech synthesis in English\n"
            "- \"video_person_prompt\": concise and clear English prompt for a video featuring a person\n"
            "- \"video_noperson_prompt\": English prompt for a background video without people\n"
            "- \"image_prompt\": English prompt for image generation"
        )
        user_message = json.dumps(inputs, ensure_ascii=False)

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=400
        )

        content = response.choices[0].message.content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise RuntimeError(f"Prompt refinement 실패: 올바른 JSON이 아닙니다. 응답 내용: {content}")

    def execute(self, raw_input: str):
        try:
            inputs = json.loads(raw_input)
        except json.JSONDecodeError:
            print("❌ JSON 입력 파싱 실패", file=sys.stderr)
            sys.exit(1)

        prompts = self.refine_all_prompts(inputs)
        print(json.dumps(prompts, ensure_ascii=False, indent=2))
        return prompts


if __name__ == "__main__":
    inputs = {
        "tts_prompt": "엄마에게 보내는 편지",
        "video_person_prompt": "햇살 아래 웃는 소녀"
    }

    refiner = PromptRefiner()
    raw_input_data = json.dumps(inputs, ensure_ascii=False)
    refiner.execute(raw_input_data)
