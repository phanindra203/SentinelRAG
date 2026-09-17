from sklearn.metrics.pairwise import cosine_similarity
from app.rag.embedder import create_embedding


def retrieve(query: str, records: list[dict], top_k: int = 1) -> list[dict]:
    query_embedding = create_embedding(query)

    document_embeddings = [
        record["embedding"]
        for record in records
    ]

    scores = cosine_similarity(
        [query_embedding],
        document_embeddings
    )[0]

    ranked_indexes = scores.argsort()[::-1]

    results = []

    for index in ranked_indexes[:top_k]:
        results.append({
            "text": records[index]["text"],
            "score": float(scores[index])
        })

    return results
