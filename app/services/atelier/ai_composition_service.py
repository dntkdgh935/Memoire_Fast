from .runway_service import generate_image_video, generate_lip_sync_video, upload_image_asset, upload_audio_asset
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

        img_id = upload_image_asset(image_url)
        audio_id = upload_audio_asset(tts)

        video = generate_lip_sync_video(image_url, tts)
        output = merge_assets(video, tts)
        return output

    elif use_tts:
        tts = generate_tts(tts_text)
        video = generate_image_video(image_url, Video_Prompt)
        output = merge_assets(video, tts)
        return output

    else:
        video = generate_image_video(image_url, Video_Prompt)
        output = merge_assets(video, None)
        return output
