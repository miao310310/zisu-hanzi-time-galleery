"""字溯后端入口。运行：uvicorn main:app --host 0.0.0.0 --port 8000"""
from contextlib import asynccontextmanager
from pathlib import Path
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
from app.chat import router as chat_router
from app.rag import init_knowledge

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_knowledge(ROOT / "data" / "characters.json")
    yield

app = FastAPI(title="字溯・汉字时光馆 API", version="1.0.0", lifespan=lifespan)
origins = [value.strip() for value in os.getenv("FRONTEND_ORIGINS", "http://127.0.0.1:5173,http://127.0.0.1:8787,http://localhost:5173,http://localhost:8787").split(",") if value.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(chat_router)

@app.get("/api/health")
def health():
    return {"ok": True, "provider": os.getenv("LLM_PROVIDER", "DeepSeek"), "model": os.getenv("LLM_MODEL", "deepseek-chat")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
