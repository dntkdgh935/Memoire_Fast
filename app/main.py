from fastapi import FastAPI
from app.api.endpoints.text2image_router import router as text2image_router
from app.api.endpoints.text2text_router import router as text2text_router

app = FastAPI()

@app.on_event("startup")
def show_routes():
    print("\n📋 등록된 라우터 목록:")
    for route in app.routes:
        if hasattr(route, "methods"):
            print(f"{list(route.methods)} {route.path}")

print("✅ text2image_router import 성공")
print("✅ text2text_router import 성공")

# 🔗 라우터 등록: 오직 이 두 개만!
app.include_router(text2image_router, prefix="/atelier", tags=["Atelier"])
app.include_router(text2text_router, prefix="/atelier", tags=["Atelier"])

@app.get("/")
async def ping():
    return {"message": "pong"}