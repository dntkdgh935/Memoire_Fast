# app/__init__.py

from app.api.endpoints.text2text_router  import router as text2text_router
from app.api.endpoints.text2image_router import router as text2image_router
from app.api.endpoints.elevenlabs_router  import router as elevenlabs_router
from app.api.endpoints.runway_router      import router as runway_router
from app.api.endpoints.openai_router      import router as openai_router
from app.api.endpoints.ffmpeg_router      import router as ffmpeg_router
from app.api.endpoints.vertex_router      import router as vertex_router
