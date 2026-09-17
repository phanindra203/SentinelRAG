from app.rag.embedder import create_embedding


def create_embedding_records(chunks: list[str]) -> list[dict]:
    records = []

    for chunk in chunks:
        embedding = create_embedding(chunk)

        records.append({
            "text": chunk,
            "embedding": embedding
        })

    return records
