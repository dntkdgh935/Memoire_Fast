import time
from openai import OpenAI, RateLimitError, OpenAIError
from app.core.config import settings
import json

class PromptRefiner:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _chat_refine(self, system_prompt: str, user_input: str, max_tokens: int = 60) -> str:
        backoff = 0.5
        for _ in range(6):
            try:
                resp = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user",   "content": user_input}
                    ],
                    temperature=0.2,
                    max_tokens=max_tokens
                )
                return resp.choices[0].message.content.strip()
            except RateLimitError:
                time.sleep(backoff)
                backoff *= 2
            except OpenAIError as e:
                raise e

        raise RateLimitError("Exceeded max retries in PromptRefiner._chat_refine")


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
            "You are a professional prompt engineer for RunwayML video generation models."
            "Rewrite the user's description into a concise, vivid English prompt optimized for generating a coherent moving scene."
            "Explicitly avoid any duplicated, distorted, or extra faces, heads, limbs, characters, text, logos, or watermarks."
            "Respond with the prompt only."
        )
        return self._chat_refine(system, raw_desc)

    # def generate_nature_sound_prompt(self,image_description):
    #     system = (
    #         "As an expert, write a clear and detailed prompt for generating natural ambient sounds, based on the provided image description."
    #         "The prompt will be used by a sound generation AI, so make sure to describe the features and qualities of the sound thoroughly."
    #     )
    #     user_prompt = f"Image description: {image_description}\n\nPrompt for generating natural ambient sounds:"
    #
    #     return self._chat_refine(system, user_prompt, max_tokens=200)


    def refine_tts_config(self, script: str, voice_gender: str) -> dict:

            system_prompt = """
    You are an expert TTS prompt engineer.
    Choose the most suitable voice_id from the ElevenLabs Starter‑plan voices listed below,
    based on the user's desired gender and the style/mood of their script.
    Use model_id "eleven_multilingual_v2" for all outputs.
    
    Also recommend two float settings **between 0.0 and 1.0**:
      • stability — controls speech consistency and pacing.  
      • similarity_boost — controls expressiveness and emotional tone.
    
    ⚠️ **Important:**  
    Do **not** always pick the extremes (0.0 or 1.0).  
    Instead, adjust stability and similarity_boost to match the script’s mood and delivery pace:  
    - For calm, steady narration, use mid-to-high stability (e.g. 0.6–0.9) and low-to-mid similarity_boost (e.g. 0.2–0.5).  
    - For energetic or emotional speech, lower stability slightly (e.g. 0.3–0.6) and raise similarity_boost (e.g. 0.6–0.9).
      
    🛑 **For voice_id**, you must output **only the raw voice ID**, with no name and no parentheses.      
    For example, if the voice is listed as:  
      - Clyde (**N2lU4FOgS3EqOtLSv0xJ**) ← Example mapping  
    Then your output must be exactly: `"N2lU4FOgS3EqOtLSv0xJ"` ← ✅  
    
    Do not output:
    - "Clyde" ← ❌
    - "Clyde (N2lU4FOgS3EqOtLSv0xJ)" ← ❌
    - "(N2lU4FOgS3EqOtLSv0xJ)" ← ❌
    
  
    Respond **only** with a JSON object exactly in this format (no extra text):
    {"voice_id":"<Voice ID>","model_id":"eleven_multilingual_v2","stability":<float>,"similarity_boost":<float>}
        
    For example, if you pick “Adam (pNInz6obpgDQGcFmaJgB)”, voice_id must be "pNInz6obpgDQGcFmaJgB", NOT "Adam".
        
    Available voices:
    - Adam (pNInz6obpgDQGcFmaJgB): deep, weighty male US accent for documentary/narration
    - Alice (Xb7hH8MSUJpSbSDYk0k2): confident female UK accent for news/tutorial
    - Antoni (ErXwobaYiN019PkySvjV): young balanced male US accent, all‑purpose
    - Arnold (VR6AewLTigWG4xSOukaG): middle‑aged male, clear for corporate/brand
    - Bill (pqHfZKP75CvOlQylNhV4): bold, mature male voice for documentary/voice‑over
    - Brian (nPczCjzI2devNBz1zQrb): low, rich mature male voice for trustworthy explanatory content
    - Callum (N2lVS1w4EtoT3dr4eOWO): rough middle‑aged male voice, US accent, for game characters or special effects
    - Charlie (IKne3meq5aSn9XLyUdCD): casual middle‑aged male Australian accent for friendly tutorials
    - Charlotte (XB0fDUnXU5powFXDhCwa): enchanting middle‑aged female Eng‑Swedish accent for cinematic/fantasy characters
    - Chris (iP95p4xoKVk53GoZ742B): comfortable middle‑aged male US accent for radio‑style content
    - Clyde (2EiwWnXFnvU5JabPnv8n): veteran warrior‑like male US accent for action/game narration
    - Daniel (onwK4e9ZLuTAKqWW03F9): deep authoritative male UK accent for news/official announcements
    - Dave (CYw3kZ02Hs0563khs1Fj): young male Bristol/Essex UK accent for friendly branded content
    - Dorothy (ThT5KcBeYPX3keUQqHPh): gentle young female UK accent for children’s stories
    - Drew (29vD33N1CtxCmqQRPOHJ): balanced middle‑aged male US accent, versatile for news/narration
    - Emily (LcfcDJNUP1GQjkzn1xUU): calm clear young female US accent for meditation/relaxation content
    - Ethan (g5CIjZEefAph4nQFvHAz): soft young male US accent for ASMR/quiet audiobooks
    - Fin (D38z5RcWu1voky8WS1ja): hearty mature male Irish accent for nautical/fantasy characters
    - Freya (jsCqWAovK2LkecY7zXl4): bright young female US accent for podcasts/vlogs
    - George (JBFqnCBsd6RMkjVDRZzb): gritty middle‑aged male UK accent for unique narration/game characters
    - Gigi (jBpfuIE2acCO8z3wKNLl): child‑like young female US accent for animation/children’s content
    - Giovanni (zcAOhNBS3c14rBihAFp1): young male with Italian inflection for foreign‑language/atmospheric content
    - Glinda (z9fAnlkpzviPz146aGWa): witch‑like fantasy middle‑aged female US accent for storytelling
    - Grace (oWAxZDx7w5VEj9dCyTzz): Southern‑tinged cheerful young female US accent for audiobooks/storytelling
    - Harry (SOYHLrjzK2X1ezoPC6cr): tense young male US accent for game characters/dramatic content
    - James (ZQe5CZNOzWyzPSCn5a3c): calm middle‑aged male Australian accent for news/documentary
    - Jeremy (bVMeCyTHy58xNoL34h3p): bright energetic young male Irish accent for presentations/ads
    - Jessie (t0jbNlBVZ17f02VDIeMI): rough middle‑aged male US accent for character voices/games
    - Joseph (Zlb1dXrM653N07WRdFW3): formal middle‑aged male UK accent for official/news content
    - Josh (TxGEqnHWrfWFTfGW9XjX): rich young male US accent for impactful narration
    - Liam (TX3LPaxmHKxFdv7VOQHJ): clean young male US accent for all‑purpose/brand content
    - Lily (pFZP5JQG7iQjIQuC4Bku): edgy middle‑aged female UK accent for character voices
    - Matilda (XrExE9yKIg1WjnnlVkGX): warm young female US accent for audiobooks/storytelling
    - Michael (flq6f7yk4E4fJM5XTYuZ): mature deep male US accent for audiobooks/documentary
    - Mimi (zrHiDhphv9ZnVXBqCLjz): playful child‑like young female accent for animation/children’s content
    - Nicole (piTKgcLEGmPE4e6mEKli): whispery intimate female US accent for ASMR/audiobooks
    - Patrick (ODq5zmih8GrVes37Dizd): forceful shouting middle‑aged male US accent for high‑energy game/ad content
    - Paul (5Q0t7uMcjvnagumLfvZi): on‑the‑scene reporter male US accent for news/documentary reporting
    - Rachel (21m00Tcm4TlvDq8ikWAM): calm clear young female US accent for soft narration
    - Sam (yoZ06aMxZJJ28mfd3POQ): rough young male US accent for unique brand/game voices
    - Sarah (EXAVITQu4vr4xnSDxMaL): smooth clear young female US accent for friendly guidance/news narration
    - Serena (pMsXgVXv3BLzUgSXRplE): gentle middle‑aged female US accent for interactive guides/chatbots
    - Thomas (GBv7mTt0atIp3Br8iCZE): calm young male US accent for meditation/relaxation content
    - Santa Claus (knrPHWnBmmDHMoiMeP3l): hearty elderly male US accent specialized for holiday/Christmas content
    """
            user_input = 'script: "{}"\nvoice_gender: "{}"'.format(
                script.replace('\\', '\\\\').replace('"', '\\"'),
                voice_gender
            )
            raw = self._chat_refine(system_prompt, user_input, max_tokens=200)
            print("🔍 raw TTS config from OpenAI:", raw)
            try:
                cfg = json.loads(raw)
            except json.JSONDecodeError as e:
                print("❌ JSON 파싱 실패:", e)
                raise
            return cfg