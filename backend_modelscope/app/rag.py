"""本地资料切分、向量化与 Chroma 检索。"""
from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
LOCAL_MODEL = ROOT / "models" / "bge-small-zh"
MODEL_ID = "BAAI/bge-small-zh-v1.5"
chroma_client = chromadb.PersistentClient(path=str(ROOT / "chroma_data"))
embedding_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    """优先复用本地模型；首次运行没有模型时使用公开模型 ID 下载。"""
    global embedding_model
    if embedding_model is None:
        source = str(LOCAL_MODEL) if LOCAL_MODEL.is_dir() else MODEL_ID
        message = "正在加载本地向量模型..." if LOCAL_MODEL.is_dir() else "首次运行，正在下载向量模型..."
        print(message)
        embedding_model = SentenceTransformer(source)
    return embedding_model


def init_knowledge(file_path: str | Path) -> None:
    path = Path(file_path)
    if not path.is_file():
        print(f"❌ 找不到文件 {path}")
        return

    raw_text = path.read_text(encoding="utf-8")
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
        length_function=len,
    )
    chunks = text_splitter.split_text(raw_text)

    try:
        chroma_client.delete_collection(name="calligraphy")
    except Exception:
        pass

    collection = chroma_client.create_collection(name="calligraphy")
    embeddings = get_embedding_model().encode(chunks, normalize_embeddings=True).tolist()
    collection.add(embeddings=embeddings, documents=chunks, ids=[str(index) for index in range(len(chunks))])
    print(f"✅ RAG 初始化成功，存入了 {len(chunks)} 条知识片段！")


def get_context(query: str) -> str:
    try:
        collection = chroma_client.get_collection(name="calligraphy")
        query_embedding = get_embedding_model().encode([query], normalize_embeddings=True).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=1)
        if results["documents"] and results["documents"][0]:
            return results["documents"][0][0]
    except Exception as error:
        print(f"检索失败: {error}")
    return "暂无相关参考资料。"
