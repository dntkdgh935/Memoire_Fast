def generate_stable_audio_file(
    prompt: str,
    duration: 15,
    num_steps: 25,
) -> str:
    # 함수 내부로 heavy import 이동
    import torch
    from diffusers import StableAudioPipeline
    from scipy.io.wavfile import write as wavwrite
    import numpy as np

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype  = torch.float16 if device=="cuda" else torch.float32

    pipe = StableAudioPipeline.from_pretrained(
        "stabilityai/stable-audio-open-1.0",
        torch_dtype=dtype
    ).to(device)

    output = pipe(
        prompt=prompt,
        audio_start_in_s=0.0,
        audio_end_in_s=float(duration),
        num_inference_steps=num_steps
    )
    # pipeline returns a list of tensors, take first and move to CPU
    audio_tensor = output.audios[0].cpu()  # shape: (T,) or (1, T)
    audio = audio_tensor.numpy().squeeze()  # ensure shape (T,)

    if audio.ndim == 2:
       audio = audio.T

    # float32 in [-1,1] → int16 in [-32767,32767]
    int16_audio = (audio * 32767).astype(np.int16)

    # write WAV at 44.1 kHz
    wavwrite("rain_audio_output.wav", 44100, int16_audio)
    print(f"✅ Generated audio saved at rain_audio_output.wav")
    return "rain_audio_output.wav"

# if __name__ == "__main__":
#     rain_and_horn_prompt = (
#         "A crystal-clear ambient recording of rain falling on pavement, "
#         "occasional distant car horns honking, with minimal noise and studio-quality fidelity"
#     )
#
#     generate_stable_audio(
#         prompt=rain_and_horn_prompt,
#         duration=15,
#         num_steps=25,
#         output_path="rain_audio_output.wav"
#     )
