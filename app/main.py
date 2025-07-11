from fastapi import FastAPI
from app.api.endpoints.atelier_router import router as atelier_router
import inspect

app = FastAPI(
    title="Memoire Project",
    description="API documentation",
    version="1.0",
)

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

@app.on_event("startup")
async def startup_event():
    print("\n📋 등록된 라우터 목록:")
    for route in app.routes:
        if hasattr(route, "methods"):
            methods = ",".join(route.methods)
            print(f"{methods:8} {route.path}")