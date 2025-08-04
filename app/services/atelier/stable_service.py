# import os
# from uuid import uuid4
#
# def generate_stable_audio_file(
#     prompt: str,
#     duration: int = 15,
#     num_steps: int = 25,
# ) -> str:
#     # 함수 내부로 heavy import 이동
#     import torch
#     from diffusers import StableAudioPipeline
#     from scipy.io.wavfile import write as wavwrite
#     import numpy as np
#
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     dtype  = torch.float16 if device=="cuda" else torch.float32
#
#     pipe = StableAudioPipeline.from_pretrained(
#         "stabilityai/stable-audio-open-1.0",
#         torch_dtype=dtype
#     ).to(device)
#
#     output = pipe(
#         prompt=prompt,
#         audio_start_in_s=0.0,
#         audio_end_in_s=float(duration),
#         num_inference_steps=num_steps
#     )
#     audio_tensor = output.audios[0].cpu()
#     audio = audio_tensor.numpy().squeeze()
#
#     if audio.ndim == 2:
#        audio = audio.T
#
#     int16_audio = (audio * 32767).astype(np.int16)
#
#     base_dir = r"C:\upload_files\audio"
#     os.makedirs(base_dir, exist_ok=True)
#
#     audio_filename = f"audio_{uuid4().hex}.wav"
#     file_path = os.path.join(base_dir, audio_filename)
#
#     wavwrite(file_path, 44100, int16_audio)
#
#     # Spring에서 매핑할 URL 경로만 리턴
#     return f"/media/audio/{audio_filename}"

