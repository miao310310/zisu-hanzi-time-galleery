#读取 knowledge.txt，把文章切段，调用本地向量模型（bge），把文本变成向量存进 Chroma 数据库；当用户提问时，根据问题把相关的段落找出来。
import os
import chromadb
from sentence_transformers import SentenceTransformer

# 加载本地模型（确保 ./models/bge-small-zh 里面有文件）
print("正在加载本地向量模型...")
embedding_model = SentenceTransformer('./models/bge-small-zh')

# 建立数据库连接
chroma_client = chromadb.PersistentClient(path="./chroma_data")


def init_knowledge(file_path: str):
    if not os.path.exists(file_path):
        print(f"❌ 找不到文件 {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    # 简单的切分（每200字一段）
    chunks = [raw_text[i:i + 200] for i in range(0, len(raw_text), 200)]

    try:
        chroma_client.delete_collection(name="calligraphy")
    except:
        pass

    collection = chroma_client.create_collection(name="calligraphy")

    # 文本转向量
    embeddings = embedding_model.encode(chunks).tolist()

    collection.add(
        embeddings=embeddings,
        documents=chunks,
        ids=[str(i) for i in range(len(chunks))]
    )
    print(f"✅ RAG 初始化成功，存入了 {len(chunks)} 条知识片段！")


def get_context(query: str) -> str:
    try:
        collection = chroma_client.get_collection(name="calligraphy")
        query_embedding = embedding_model.encode([query]).tolist()
        results = collection.query(query_embeddings=query_embedding, n_results=1)

        if results['documents'] and len(results['documents'][0]) > 0:
            return results['documents'][0][0]
    except Exception as e:
        print(f"检索失败: {e}")
    return "暂无相关参考资料。"