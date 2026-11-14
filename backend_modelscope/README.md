# 字溯 ModelScope RAG 后端

这是字溯当前本机演示使用的 FastAPI + ChromaDB + ModelScope API 后端源码。

## 不包含的本机数据

仓库不会提交 `.env`、`.venv`、`models/` 或 `chroma_data/`。首次运行会按代码配置下载嵌入模型，并在本地建立向量库。

## 本地启动

建议使用 Python 3.11：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

在 `.env` 中仅填写一行真实 Token：

```env
MODELSCOPE_API_KEY=ms-你的真实Token
```

不要提交或分享 `.env`。启动后 API 地址为 `http://127.0.0.1:8000`，根目录 Vue 前端可通过 `VITE_API_MODE=api` 和 `/api` 代理连接它。

## 资料来源

`knowledge.txt` 是当前 RAG 检索资料。模型回答中的引用链接会回到该文件，便于评委核查。
