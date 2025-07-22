import os
# app/services/atelier/prompt_refiner.py

import json
from openai import OpenAI
from app.core.config import settings

class PromptRefiner:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _chat_refine(self, system_prompt: str, user_input: str, max_tokens: int = 60) -> str:
        resp = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",  "content": system_prompt},
                {"role": "user",    "content": user_input}
            ],
            temperature=0.2,
            max_tokens=max_tokens
        )
        return resp.choices[0].message.content.strip()

    def refine_image_prompt(self, raw_prompt: str) -> str:
        system = (
            "You are a professional prompt engineer for image generation APIs. "
            "Rewrite the user’s description into a concise, vivid English prompt "
            "optimized for DALL·E (gpt-image-1). Respond with the prompt only."
        )
        return self._chat_refine(system, raw_prompt)

    def refine_tts_prompt(self, raw_text: str) -> str:
        system = (
            "You are an expert in voice a:wnd TTS prompt crafting. "
            "Rewrite the user’s text into a natural, expressive English script "
            "suitable for speech synthesis. Respond with the script only."
        )
        return self._chat_refine(system, raw_text, max_tokens=150)

    def refine_video_person_prompt(self, raw_desc: str) -> str:
        system = (
            "You are a video prompt specialist for scenes with people. "
            "Convert the user’s description into a clear, concise English prompt "
            "for a video generation API, emphasizing the person’s actions and environment."
        )
        return self._chat_refine(system, raw_desc)

    def refine_video_background_prompt(self, raw_desc: str) -> str:
        system = (
            "You specialize in background-only video prompts. "
            "Turn the user’s description into an English prompt "
            "for a video generation API, focusing on scenery and atmosphere."
        )
        return self._chat_refine(system, raw_desc)

    def generate_nature_sound_prompt(self,image_description):
        system_prompt = (
            "너는 이미지를 설명한 텍스트를 기반으로 자연 환경음을 생성하기 위한 구체적이고 명확한 프롬프트를 작성하는 전문가야. "
            "최종 프롬프트는 음향 생성 AI에게 전달될 예정이므로, 사운드의 특징을 상세히 묘사해야 해."
        )
        user_prompt = f"이미지 설명: {image_description}\n\n자연 환경음 생성용 프롬프트:"

        response = self.client.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=200,
        )

        sound_prompt = response.choices[0].message.content
        return sound_prompt

