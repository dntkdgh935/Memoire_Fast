from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints.text2text_router import router as text_router
import app.api.endpoints.text2image_router as image_router_module
import os


app = FastAPI()

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

# ✅ 라우터 한 번씩만 등록
app.include_router(text_router, prefix="/atelier", tags=["Atelier"])
app.include_router(image_router_module.router, prefix="/atelier")

@app.on_event("startup")
def show_routes():
    print("\n📋 [DEBUG] 등록된 라우터 목록:")
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"➡️ method={route.methods}, path={route.path}")

@app.get("/")
async def ping():
    return {"message": "pong"}