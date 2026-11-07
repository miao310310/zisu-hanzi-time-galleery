#相当于大厦的“总电闸”。把 chat.py 里的路由注册进去，启动时顺便调用一下 rag.py 把文本存进数据库。
from dotenv import load_dotenv
import os

# 必须在导入其他模块前加载环境变量
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.chat import router as chat_router
from app.rag import init_knowledge

app = FastAPI(title="字溯・汉字时光馆 API")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn

    print("🚀 正在启动服务器...")

    # 启动前初始化知识库
    init_knowledge("knowledge.txt")

    uvicorn.run(app, host="127.0.0.1", port=8000)