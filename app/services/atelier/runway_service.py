import requests
import os
from app.core.config import settings
from runwayml import RunwayML, TaskFailedError

client = RunwayML()


# Create a new image-to-video task using the "gen4_turbo" model

def generate_video():
  try:
    task = client.image_to_video.create(
      model='Gen-3 Alpha Turbo',
      # Point this at your own image file
      prompt_image='https://example.com/image.jpg',
      prompt_text='Generate a video',
      ratio='1280:720',
      duration=5,
    ).wait_for_task_output()

    print('Task complete:', task)
  except TaskFailedError as e:
    print('The video failed to generate.')
    print(e.task_details)



