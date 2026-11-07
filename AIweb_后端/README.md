# 字溯・汉字时光馆 (后端部分)

## 📖 项目简介
本项目为“传智杯 AI-WEB 挑战赛”参赛作品的后端服务。基于 FastAPI 构建，专为“汉字源流与书法科普”设计。
核心功能包含：
- 本地化 RAG（检索增强生成）知识库问答
- AI Agent 工具调用（Function Calling）实现智能查字
- 严格的话题拦截与安全护栏
- SSE 流式打字机响应

## 🛠️ 技术栈
- Python 3.10+
- FastAPI
- ChromaDB (本地向量库)
- ModelScope API (Qwen 大模型)

## 🚀 快速启动指南 (评委/开发者请看这里)

1. **安装依赖**：
   ```bash
   pip install -r requirements.txt