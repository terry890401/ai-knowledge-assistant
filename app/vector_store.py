import chromadb
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rank_bm25 import BM25Okapi

load_dotenv()

chroma_client = chromadb.CloudClient(
  api_key=os.getenv("CHROMA_API_KEY"),
  tenant=os.getenv("CHROMA_TENANT"),
  database=os.getenv("CHROMA_DATABASE")
)

# 使用 OpenAI embedding
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)

# 取得或建立 collection
collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=openai_ef
)

def add_document(document_id: int, text: str, filename: str):
    # 切割文件
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_text(text)
    
    # 存進 Chroma
    collection.add(
        ids=[f"{document_id}_{i}" for i in range(len(chunks))],
        documents=chunks,
        metadatas=[{"document_id": document_id, "filename": filename} for _ in chunks]
    )

def search_documents(query: str, user_document_ids: list[int], n_results: int = 3) -> list[str]:
    # 原本的純向量搜尋（保留備用）
    if not user_document_ids:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
        where={"document_id": {"$in": user_document_ids}}
    )
    return results["documents"][0] if results["documents"] else []

def hybrid_search(query: str, user_document_ids: list[int], n_results: int = 3) -> list[dict]:
    if not user_document_ids:
        return []

    vector_results = collection.query(
        query_texts=[query],
        n_results=n_results * 2,
        where={"document_id": {"$in": user_document_ids}},
        include=["documents", "metadatas"]  # ← 加上 metadatas
    )

    vector_docs = vector_results["documents"][0] if vector_results["documents"] else []
    vector_metas = vector_results["metadatas"][0] if vector_results["metadatas"] else []

    if not vector_docs:
        return []

    tokenized_docs = [doc.split() for doc in vector_docs]
    bm25 = BM25Okapi(tokenized_docs)
    bm25_scores = bm25.get_scores(query.split())

    scored = sorted(
        zip(vector_docs, vector_metas, bm25_scores),
        key=lambda x: x[2],
        reverse=True
    )

    # 回傳 dict，包含內容和來源 document_id
    return [
        {"content": doc, "document_id": meta.get("document_id"), "filename": meta.get("filename")}
        for doc, meta, score in scored[:n_results]
    ]

def delete_document(document_id: int):
    # 取得這個文件的所有 chunk id
    results = collection.get(where={"document_id": document_id})
    if results["ids"]:
        collection.delete(ids=results["ids"])