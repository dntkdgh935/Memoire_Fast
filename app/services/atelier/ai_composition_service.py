from .runway_service import generate_video
from .audiogen_service import generate_music
from .elevenlabs_service import create_voice
from .ffmpeg_service import merge_assets

def compose_video(
    image_url: str,
    bg_prompt: str,
    music_prompt: str,
    tts_text: str
) -> str:
    bg_vid   = generate_video(bg_prompt)
    music    = generate_music(music_prompt)
    tts      = create_voice(tts_text)

    output = merge_assets(bg_vid, music, tts, "final.mp4")
    return output
