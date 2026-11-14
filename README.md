# 字溯 · 汉字时光馆

面向汉字源流与书法学习的 Vue 3 + Vite Web 应用。项目正式后端统一为 **ModelScope + ChromaDB RAG**，前端通过 SSE 接收流式回答与资料来源。

## 项目结构

```text
src/                   Vue 页面、组件、数据和 API 客户端
public/images/         六大书体与作品赏析素材
tests/                 前端流式解析测试
backend_modelscope/    FastAPI + ModelScope + ChromaDB RAG 正式后端
.github/workflows/     GitHub Pages 静态前端部署
```

## 前端本地运行

需要 Node.js 20 或 22：

```powershell
npm ci
npm run dev
```

质量检查与生产构建：

```powershell
npm test
npm run build
```

## 魔塔 RAG 后端

建议使用 Python 3.11。在一个终端中启动后端：

```powershell
cd backend_modelscope
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python main.py
```

在 `backend_modelscope/.env` 中填写真实密钥，且只保留这一行：

```env
MODELSCOPE_API_KEY=ms-你的真实Token
```

后端默认运行在 `http://127.0.0.1:8000`。首次启动会下载嵌入模型并建立本地向量库，耗时取决于网络；`.env`、`.venv`、`models/` 和 `chroma_data/` 都不会提交到 GitHub。

> ModelScope 返回 401 或 403 时，优先检查 Token、邮箱验证和阿里云账号绑定状态；这些是服务商账户要求，不要把 Token 写进源码或上传到仓库。

## 前后端联调

复制根目录 `.env.example` 为 `.env.local`，把以下值改为 `api` 后重启 `npm run dev`：

```env
VITE_API_MODE=api
VITE_API_BASE=/api
```

Vite 会将 `/api` 自动代理到本机 `http://127.0.0.1:8000`。前端发送 `question`、`context` 与 `history`，后端返回标准 SSE 事件：`delta`、`sources`、`done` 或 `error`。

## 公网演示与边界

GitHub Pages 只托管静态前端，因此公开地址保持 Demo 模式，不能直接运行 Python、ChromaDB 或使用你的 ModelScope 密钥。要发布真实问答，需将 `backend_modelscope/` 独立部署到支持 Python 的服务，并为前端配置可访问的 API 地址。

## 主要功能

- 六大书体导航、字体专题和作品赏析。
- 汉字演变浏览、田字格笔顺观察与临写练习。
- 本地收藏、最近浏览与学习上下文携带。
- RAG 检索增强的书法问答、流式输出和资料来源展示。

资料仍需在提交参赛前逐条完成来源核验；页面中的古文字示意不得作为考证结论使用。
