import os
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from app.rag import get_context
from pathlib import Path
from dotenv import load_dotenv

# 1. 强制加载根目录下的 .env 文件
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# 2. 创建路由对象
router = APIRouter()

# 3. 初始化魔搭客户端
client = OpenAI(
    api_key=os.getenv("MODELSCOPE_API_KEY"),
    base_url="https://api-inference.modelscope.cn/v1"
)

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
                    "char": {
                        "type": "string",
                        "description": "要查询的汉字，例如'龙'或'日'"
                    }
                },
                "required": ["char"]
            }
        }
    }
]


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    prompt: str
    history: List[Message] = []


# 拦截词
ALLOW_WORDS = {"字", "汉字", "甲骨文", "金文", "小篆", "隶书", "楷书", "行书", "草书", "书法", "碑帖", "临摹", "演变",
               "字体", "曹全碑", "毛公鼎"}
BLOCK_WORDS = {"游戏", "恋爱", "作业", "数学", "天气", "美食", "写代码"}


def check_topic(text: str) -> bool:
    for w in BLOCK_WORDS:
        if w in text: return False
    if not any(w in text for w in ALLOW_WORDS) and len(text) > 10:
        return False
    return True


@router.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    user_text = req.prompt

    # 1. 安全拦截
    if not check_topic(user_text):
        def reject():
            yield "您好，我是「字溯」专属书法助手。我仅专注于汉字源流、书法碑帖的科普，暂时无法解答其他问题哦。"

        return StreamingResponse(reject(), media_type="text/event-stream")

    # 2. 组装提示词
    system_prompt = "你是「字溯」专属科普助手。请严格根据提供的参考资料回答，如果资料里没有，就说不知道，不要瞎编。"
    messages = [{"role": "system", "content": system_prompt}]
    for msg in req.history:
        messages.append({"role": msg.role, "content": msg.content})

    def generate():
        try:
            print(f"\n========== 收到新提问: {user_text} ==========")

            # 3. 先走基础 RAG 查资料
            context = get_context(user_text)
            print(f"🔍 [RAG检索结果]: {context}")

            final_prompt = f"参考资料：\n{context}\n\n用户问题：{user_text}"
            messages.append({"role": "user", "content": final_prompt})

            print("📡 第一次请求大模型（判断意图）...")

            # 4. 带着 tools 请求大模型
            response = client.chat.completions.create(
                model="Qwen/Qwen3.8-27B",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message

            # 5. 判断是否调用工具
            if response_message.tool_calls:
                print("🤖 [Agent 决策] 发现大模型需要调用工具！")
                tool_call = response_message.tool_calls[0]
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                if function_name == "lookup_character_image":
                    search_char = arguments.get("char", "")
                    print(f"🔧 [Agent 执行] 正在查询汉字：{search_char}")

                    tool_result = f"成功找到 {search_char} 的数据。{context}"

                    messages.append(response_message)
                    messages.append({
                        "role": "tool",
                        "content": tool_result,
                        "tool_call_id": tool_call.id
                    })

                    print("📡 第二次请求大模型（结合工具结果生成回答）...")
                    final_response = client.chat.completions.create(
                        model="Qwen/Qwen3.8-27B",
                        messages=messages,
                        stream=True
                    )

                    for chunk in final_response:
                        if chunk.choices and chunk.choices[0].delta.content:
                            content = chunk.choices[0].delta.content
                            print(content, end="", flush=True)
                            yield content
            else:
                print("💬 [Agent 决策] 正常对话，无需调用工具。")
                stream_response = client.chat.completions.create(
                    model="Qwen/Qwen3.8-27B",
                    messages=messages,
                    stream=True
                )
                for chunk in stream_response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        print(content, end="", flush=True)
                        yield content

            print("\n========== 回答结束 ==========\n")

        except Exception as e:
            print(f"❌ 发生错误: {e}")
            yield f"服务异常: {str(e)}"

    return StreamingResponse(generate(), media_type="text/event-stream")