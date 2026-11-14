import os
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from openai import OpenAI
from app.rag import get_context
from pathlib import Path
from dotenv import load_dotenv

# 1. 强制加载根目录下的 .env 文件
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# 2. 创建路由对象
router = APIRouter()

def model_client() -> OpenAI:
    """在真正调用时读取 Token，避免公开源码在未配置 .env 时导入失败。"""
    token = os.getenv("MODELSCOPE_API_KEY")
    if not token or token == "your_api_key_here":
        raise RuntimeError("MODELSCOPE_API_KEY 未配置，请在根目录 .env 中填写真实 Token。")
    return OpenAI(api_key=token, base_url="https://api-inference.modelscope.cn/v1")

# 4. Agent 工具定义
tools = [
    {
        "type": "function",
        "function": {
            "name": "lookup_character_image",
            "description": "当用户想查询某个具体汉字的演变、甲骨文/金文图片链接时，调用此工具。",
            "parameters": {
                "type": "object",
                "properties": {
                    "char": {"type": "string", "description": "要查询的汉字，例如'龙'或'日'"}
                },
                "required": ["char"]
            }
        }
    }
]


# ================= 数据模型 =================
class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: Optional[str] = None
    prompt: Optional[str] = None
    message: Optional[str] = None
    text: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}
    history: Optional[List[Message]] = []


# ================= 查字典接口 =================
@router.get("/api/characters/{char}")
async def get_character(char: str):
    return {
        "character": char,
        "pinyin": f"{char} (拼音)",
        "evolution": "甲骨文 -> 金文 -> 小篆 -> 隶书 -> 楷书",
        "description": f"这是'{char}'字的演变介绍（后端模拟数据）。",
        "image": "/static/dragon.jpg"
    }


# ================= 核心聊天接口 =================
@router.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_text = req.question or req.prompt or req.message or req.text or ""

    if not user_text:
        return StreamingResponse(
            iter(["event: error\ndata: {\"message\": \"未收到有效提问\"}\n\n"]),
            media_type="text/event-stream"
        )

    # 组装提示词
    system_prompt = "你是「字溯」专属科普助手。请严格根据提供的参考资料回答。回答完毕后，必须另起一行，加上【参考来源：字溯资料库】。如果资料里没有，就说不知道，不要瞎编。"
    messages = [{"role": "system", "content": system_prompt}]

    if req.history:
        for msg in req.history:
            messages.append({"role": msg.role, "content": msg.content})

    def generate():
        try:
            print(f"\n========== 收到新提问: {user_text} ==========")

            # 3. RAG 查资料
            context = get_context(user_text)
            print(f"🔍 [RAG检索结果]: {context}")

            final_prompt = f"参考资料：\n{context}\n\n用户问题：{user_text}"
            messages.append({"role": "user", "content": final_prompt})

            # 4. 请求大模型
            stream_response = model_client().chat.completions.create(
                model="Qwen/Qwen3.8-27B",
                messages=messages,
                stream=True
            )

            # 👈 终极完美适配：既带 event: delta，data 又是合法 JSON！
            for chunk in stream_response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    print(content, end="", flush=True)

                    # 构造前端期望的 JSON：{"text": "xxx"}
                    json_str = json.dumps({"text": content}, ensure_ascii=False)

                    # 发送 event: delta，data: 对应的 JSON，并以 \n\n 结尾
                    yield f"event: delta\ndata: {json_str}\n\n"

            # 先发送来源，再发送完成事件，便于前端完整渲染引用卡片。
            sources_data = json.dumps({
                "sources": [
                    {
                        "title": "《汉字六大字体资料汇编》· 字溯资料库",
                        "url": "https://github.com/miao310310/zisu-hanzi-time-galleery/blob/main/backend_modelscope/knowledge.txt",
                        "excerpt": f"根据资料库检索：{context[:80]}..."  # 截取原文前80字作为摘要
                    }
                ]
            }, ensure_ascii=False)
            yield f"event: sources\ndata: {sources_data}\n\n"
            yield "event: done\ndata: [DONE]\n\n"
            print("\n========== 回答结束 ==========\n")

        except Exception as e:
            print(f"❌ 发生错误: {e}")
            error_json = json.dumps({"message": "AI 服务暂不可用，请检查 ModelScope 账号、Token 与网络后重试。"}, ensure_ascii=False)
            yield f"event: error\ndata: {error_json}\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")
