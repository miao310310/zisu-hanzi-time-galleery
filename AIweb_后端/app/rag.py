"""小型、可溯源的本地 RAG。"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any
import chromadb
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parents[1]
_client = chromadb.PersistentClient(path=str(ROOT / "chroma_data"))
_collection = None
_model = None
_records: list[dict[str, Any]] = []

def _embedding_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-zh-v1.5"))
    return _model

def init_knowledge(file_path: Path) -> None:
    global _collection, _records
    with file_path.open("r", encoding="utf-8") as file:
        _records = json.load(file)
    documents, metadatas, ids = [], [], []
    for record in _records:
        documents.append("汉字：" + record["character"] + "\n" + "\n".join(record.get("rag_chunks") or [record["description"]]))
        source = (record.get("sources") or [{}])[0]
        metadatas.append({"source_title": source.get("title", "字溯资料库"), "source_url": source.get("url", "")})
        ids.append(record["id"])
    try:
        _client.delete_collection("zisu_knowledge")
    except Exception:
        pass
    _collection = _client.create_collection("zisu_knowledge")
    _collection.add(ids=ids, documents=documents, embeddings=_embedding_model().encode(documents, normalize_embeddings=True).tolist(), metadatas=metadatas)
    print(f"RAG 已加载 {len(documents)} 条可溯源资料。")

def get_character(character: str) -> dict[str, Any] | None:
    return next((item for item in _records if item["character"] == character), None)

def search(query: str, limit: int = 3) -> tuple[str, list[dict[str, str]]]:
    if _collection is None:
        return "资料库尚未初始化。", []
    result = _collection.query(query_embeddings=_embedding_model().encode([query], normalize_embeddings=True).tolist(), n_results=min(limit, len(_records)), include=["documents", "metadatas"])
    sources: list[dict[str, str]] = []
    for metadata in result.get("metadatas", [[]])[0]:
        source = {"title": metadata.get("source_title", "字溯资料库"), "url": metadata.get("source_url", "")}
        if source not in sources:
            sources.append(source)
    return "\n\n".join(result.get("documents", [[]])[0]), sources
