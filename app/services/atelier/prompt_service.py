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
            "Rewrite the user’s description into a concise, vivid English prompt optimized for DALL·E (gpt-image-1). "
            "Start your prompt with 'In the mood of the original image,' and ensure that the overall feeling and atmosphere are preserved. "
            "Respond with the prompt only."
        )
        return self._chat_refine(system, raw_prompt)

    def refine_tts_prompt(self, raw_text: str) -> str:
        system = (
            "You are an expert in voice a:wnd TTS prompt crafting. "
            "Rewrite the user’s text into a natural, expressive English script "
            "suitable for speech synthesis. Respond with the script only."
        )
        return self._chat_refine(system, raw_text, max_tokens=150)


    def refine_video_background_prompt(self, raw_desc: str) -> str:
        system = (
            "You are a professional prompt engineer for image generation APIs. "
            "Rewrite the user's description into a concise, vivid English prompt optimized for DALL·E (gpt-image-1). "
            "Start your prompt with 'In the mood of the original image,' and ensure that the overall feeling and atmosphere are preserved. "
            "Explicitly avoid any duplicated, distorted, or extra faces, heads, limbs, or characters. "
            "Only depict a natural, realistic scene based on the user's intent. "
            "Respond with the prompt only."
        )
        return self._chat_refine(system, raw_desc)

    def generate_nature_sound_prompt(self,image_description):
        system = (
            "As an expert, write a clear and detailed prompt for generating natural ambient sounds, based on the provided image description."
            "The prompt will be used by a sound generation AI, so make sure to describe the features and qualities of the sound thoroughly."
        )
        user_prompt = f"Image description: {image_description}\n\nPrompt for generating natural ambient sounds:"

        return self._chat_refine(system, user_prompt, max_tokens=200)


