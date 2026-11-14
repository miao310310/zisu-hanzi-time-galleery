# 字溯 · 汉字时光馆

Vue3 + Vite + Vue Router + Pinia 前端原型。四个路由：`/`、`/explore`、`/study`、`/chat`。使用 hash 路由，静态托管无需配置路径回退。

## 运行
安装 Node.js 20 或 22 后，在此目录执行：
```sh
npm ci
npm run dev
npm test
npm run build
```
开发服务终端会显示本地地址。构建产物位于 dist，可直接静态部署。

## 功能与边界
- 字体分类、详情和携带上下文提问。
- 汉字查询、收藏、最近浏览（Pinia + localStorage）。
- 田字格观察、浓度调整、测验计分。
- 聊天演示；接口模式支持 POST SSE、停止、重试、引用。
- 默认 demo，仅四个汉字、预设回答；没有真实 RAG、模型或历史字形图片。资料未完成学术校对。
- 字匣本地持久化，聊天暂不跨路由保存。卡片大字是现代装饰字，并非古文字拓片。

## 后端联调
复制 `.env.example` 为 `.env.local`，改为 `VITE_API_MODE=api`，重启开发服务。`VITE_API_BASE=/api`。开发代理默认转发到 http://127.0.0.1:8000，可用环境变量 API_PROXY_TARGET 修改。生产环境由同源反向代理转发 /api，或使用允许 CORS 的后端地址重新构建。

前端不保存模型密钥；模型调用、领域控制与检索均由 B 的后端实现。

### GET /api/characters/{character}
成功返回：
```json
{"id":"ri","character":"日","description":"资料正文","sources":[{"title":"来源标题","url":"https://example.org/document","excerpt":"相关摘录"}]}
```
示例 URL 仅说明格式，不是真实资料。未收录返回 404。

### POST /api/chat
请求：
```json
{"question":"请解读日字","context":{"character":"日","script":null,"document_ids":["ri"]}}
```
响应 Content-Type: text/event-stream。每个事件以空行结束：
```text
event: delta
data: {"text":"日字"}

event: sources
data: {"sources":[{"title":"来源标题","url":"https://example.org/document"}]}

event: done
data: {}

```
错误事件：`event: error`，data 为 `{"message":"错误原因"}`。客户端主动停止会取消请求；服务端应同步释放模型流。代理需关闭响应缓冲。

## 目录
src/pages 页面；src/components 通用组件；src/stores 字匣状态；src/services 请求与流解析；src/data.js 本地演示资料；tests 流解析测试。

## 后端源码说明

- `backend_modelscope/`：当前本机演示使用的 ModelScope + ChromaDB RAG 后端。它只提交可审查的源码、资料与示例配置；`.env`、模型、向量库和虚拟环境均被忽略。
- `AIweb_后端/`：保留的 OpenAI 兼容接口后端实现，可通过 `LLM_PROVIDER`、`LLM_BASE_URL` 与 `LLM_MODEL` 切换模型服务。

前端公开演示默认使用本地 demo 模式；GitHub Pages 是静态托管，不能直接运行上述 Python 后端。要启用真实问答，请在本机或独立服务器部署其中一个后端，再将前端的 `VITE_API_MODE` 设为 `api`。

## 本机 DeepSeek 问答
1. 在 server/.env 中填入 DEEPSEEK_API_KEY（不要发送到聊天或提交仓库）。默认模型 deepseek-flash，可按账号支持情况修改 DEEPSEEK_MODEL。
2. 前端 .env.local 设置 VITE_API_MODE=api、VITE_API_BASE=/api，再 npm run build。
3. npm start，访问 http://127.0.0.1:8787/#/chat 。此服务同时提供前端与 /api，不要使用旧的 8765 静态端口进行 AI 问答。
4. 后端每次请求读取配置，保存密钥后无需重启。模型请求会使用账号的 API 额度。
5. 当前只支持模型问答与最近 12 条对话历史，没有 RAG。系统提示词用于引导话题，不代表绝对防绕过保证。
6. 本地服务仅绑定回环地址。公开部署前需要接入身份认证、配额与更完整的日志及限流。
官方文档：https://api-docs.deepseek.com/
