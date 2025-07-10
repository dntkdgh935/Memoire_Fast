from fastapi import FastAPI
from app.api.endpoints.atelier_router import router as atelier_router
from app.api.endpoints.text2image_router import router as text2image_router  # 디버깅용
import inspect

app = FastAPI()

@app.on_event("startup")
def show_routes():
    print("\n📋 등록된 라우터 목록:")
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"{list(route.methods)} {route.path}")

print("✅ text2image_router import 성공")
print("✅ atelier_router import 성공")

app.include_router(atelier_router, prefix="/atelier", tags=["Atelier"])

@app.get("/")
async def ping():
    return {"message": "pong"}