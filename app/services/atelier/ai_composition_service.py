from .runway_service import generate_image_video, generate_lip_sync_video, upload_image_asset, upload_audio_asset
from .audiogen_service import generate_music_mubert
from .elevenlabs_service import generate_tts
from .ffmpeg_service import merge_assets

def compose_video(
    image_url: str,
    TTS_Prompt: str,
    Video_Prompt: str,
    music_prompt: str,
    tts_text: str,
    is_person: bool,
    use_tts: bool,
) :
    if is_person:
        tts = generate_tts(tts_text)
        music = generate_music_mubert(music_prompt)

        img_id = upload_image_asset(image_url)
        audio_id = upload_audio_asset(tts)

        video = generate_lip_sync_video(image_url, tts)
        output = merge_assets(video, music, tts)
        return output

    elif use_tts:
        tts = generate_tts(tts_text)
        music = generate_music_mubert(music_prompt)
        video = generate_image_video(image_url, Video_Prompt)
        output = merge_assets(video, music, tts)
        return output

    else:
        music = generate_music_mubert(music_prompt)
        video = generate_image_video(image_url, Video_Prompt)
        output = merge_assets(video, music, None)
        return output
