from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints.atelier_router import router as atelier_router
from fastapi.routing import APIRoute
from app.api.endpoints.text2text_router import router as text_router
from app.api.endpoints.face_recognition_router import router as face_recognition_router
import app.api.endpoints.text2image_router as image_router_module
from contextlib import asynccontextmanager

from app.api.endpoints.tarot_router import router as tarot_router
import os
from fastapi.staticfiles import StaticFiles

import logging





logging.basicConfig(level=logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버가 올라갈 때 한 번 실행
    print("\n📋 [DEBUG] 등록된 라우터 목록:")
    for route in app.routes:
        if isinstance(route, APIRoute):
            print(f"➡️ {route.methods} {route.path}")
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(atelier_router)

app.include_router(tarot_router)

# ✅ 라우터 한 번씩만 등록
app.include_router(text_router, prefix="/atelier", tags=["Atelier"])
app.include_router(image_router_module.router, prefix="/atelier")


app.include_router(face_recognition_router)

from app.api.endpoints.library_router import router as library_router
app.include_router(library_router, prefix="/library", tags=["Library"])

app.mount("/memory_video", StaticFiles(directory="C:/upload_files/memory_video"), name="memory_video")
app.mount( "/upload_files", StaticFiles(directory="C:/upload_files"), name="upload_files")
app.mount(
    "/upload_files/tts",
    StaticFiles(directory="C:/upload_files/tts"),
    name="tts"
)
@app.get("/")
async def ping():
    return {"message": "pong"}

# .\.venv\Scripts\Activate.ps1 터미널에서 환경 설정한 곳으로 설정
# uvicorn app.main:app --reload 라우터 확인
# (.venv) PS D:\python_workspace\FastAPI> $env:PYTHONPATH="D:\python_workspace\FastAPI"
# (.venv) PS D:\python_workspace\FastAPI> python app/main.py