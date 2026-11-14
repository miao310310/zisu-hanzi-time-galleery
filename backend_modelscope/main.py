from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.chat import router as chat_router
from app.rag import init_knowledge

app = FastAPI(title="字溯・汉字时光馆 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. 先挂载静态资源
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

# 2. 注册 API 接口
app.include_router(chat_router)

# 3. 最后挂载前端页面
frontend_dir = ROOT / "frontend"
if frontend_dir.is_dir():
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    init_knowledge(ROOT / "knowledge.txt")
    uvicorn.run(app, host="0.0.0.0", port=8000)
