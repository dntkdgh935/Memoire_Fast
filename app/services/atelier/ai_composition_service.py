from .d_id_service    import generate_facial_animation
from .runway_service import generate_background
from .audiogen_service import generate_music
from .elevenlabs_service import generate_tts
from .ffmpeg_service import merge_assets

def compose_video(
    image_url: str,
    bg_prompt: str,
    music_prompt: str,
    tts_text: str
) -> str:
    face_vid = generate_facial_animation(image_url)
    bg_vid   = generate_background(bg_prompt)
    music    = generate_music(music_prompt)
    tts      = generate_tts(tts_text)

    output = merge_assets(face_vid, bg_vid, music, tts, "final.mp4")
    return output
