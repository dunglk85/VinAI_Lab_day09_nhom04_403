"""
build_index.py — Xây dựng ChromaDB index từ tài liệu nội bộ.
Chạy 1 lần để populate vector store.
"""
import os
import chromadb
from sentence_transformers import SentenceTransformer

DOCS_DIR = "./data/docs"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "day09_docs"
CHUNK_SIZE = 500  # ký tự tối đa mỗi chunk
CHUNK_OVERLAP = 100  # overlap giữa 2 chunks liền kề


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Chia văn bản thành các đoạn nhỏ (chunks) với overlap."""
    # Chia theo đoạn (paragraph) trước, nếu đoạn quá dài thì cắt thêm
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 1 <= chunk_size:
            current = current + "\n" + para if current else para
        else:
            if current:
                chunks.append(current.strip())
            # Nếu paragraph đơn lẻ vẫn quá dài, cắt nhỏ hơn
            if len(para) > chunk_size:
                words = para.split()
                sub = ""
                for w in words:
                    if len(sub) + len(w) + 1 <= chunk_size:
                        sub = sub + " " + w if sub else w
                    else:
                        if sub:
                            chunks.append(sub.strip())
                        sub = w
                if sub:
                    current = sub
            else:
                current = para

    if current:
        chunks.append(current.strip())

    return chunks


def main():
    print("=" * 60)
    print("Building ChromaDB index for Day 09 Lab")
    print("=" * 60)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Xóa collection cũ nếu có, tạo mới
    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"Deleted old collection '{COLLECTION_NAME}'")
    except Exception:
        pass

    collection = client.create_collection(
        COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    doc_count = 0
    chunk_count = 0

    for fname in sorted(os.listdir(DOCS_DIR)):
        fpath = os.path.join(DOCS_DIR, fname)
        if not os.path.isfile(fpath):
            continue

        with open(fpath, encoding="utf-8") as f:
            content = f.read()

        chunks = chunk_text(content)
        doc_count += 1

        print(f"\n📄 {fname}: {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            chunk_id = f"{fname}_chunk_{i:03d}"
            embedding = model.encode([chunk])[0].tolist()

            collection.add(
                ids=[chunk_id],
                documents=[chunk],
                embeddings=[embedding],
                metadatas=[{
                    "source": fname,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }]
            )
            print(f"  [{i}] {chunk[:60]}...")
            chunk_count += 1

    print(f"\n✅ Indexed {chunk_count} chunks from {doc_count} documents.")
    print(f"   Collection '{COLLECTION_NAME}' count: {collection.count()}")


if __name__ == "__main__":
    main()
