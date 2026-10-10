from app.retriever import search_documents


# ==========================================
# RAG Evaluation Dataset
# ==========================================

EVALUATION_DATASET = [
    {
        "question": "What is a Kubernetes Deployment?",
        "expected_source": "kubernetes.md",
        "expected_chunk_id": "9",
    },
    {
        "question": "What is a Kubernetes Pod?",
        "expected_source": "kubernetes.md",
        "expected_chunk_id": "9",
    },
    {
        "question": "What does a Kubernetes Service provide?",
        "expected_source": "kubernetes.md",
        "expected_chunk_id": "10",
    },
    {
        "question": "What is Terraform remote state?",
        "expected_source": "terraform.md",
        "expected_chunk_id": "11",
    },
    {
        "question": "Why use Azure Blob Storage for Terraform state?",
        "expected_source": "terraform.md",
        "expected_chunk_id": "11",
    },
    {
        "question": "What is the typical Terraform workflow?",
        "expected_source": "terraform.md",
        "expected_chunk_id": "12",
    },
    {
        "question": "What is the architecture of an AKS cluster?",
        "expected_source": "aks.md",
        "expected_chunk_id": "1",
    },
    {
        "question": "What is an AKS node pool?",
        "expected_source": "aks.md",
        "expected_chunk_id": "2",
    },
    {
        "question": "How does AKS integrate with Azure Container Registry?",
        "expected_source": "aks.md",
        "expected_chunk_id": "4",
    },
    {
        "question": "How does AKS use managed identities?",
        "expected_source": "aks.md",
        "expected_chunk_id": "5",
    },
]


# ==========================================
# Evaluation
# ==========================================

def evaluate():

    total_questions = len(EVALUATION_DATASET)

    retrieval_hits = 0
    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0

    reciprocal_rank_sum = 0.0

    print("\n")
    print("=" * 70)
    print("SentinelRAG - RAG Retrieval Evaluation")
    print("=" * 70)

    for index, test_case in enumerate(EVALUATION_DATASET, start=1):

        question = test_case["question"]
        expected_source = test_case["expected_source"]
        expected_chunk_id = test_case["expected_chunk_id"]

        print("\n")
        print("-" * 70)
        print(f"Test {index}/{total_questions}")
        print(f"Question: {question}")
        print("-" * 70)

        results = search_documents(question, top_k=5)

        found_rank = None

        for rank, result in enumerate(results, start=1):

            source = result.get("filename")
            chunk_id = str(result.get("id"))

            hybrid_score = result.get("score")
            reranker_score = result.get("reranker_score")

            print(f"\nRank {rank}")
            print(f"Source: {source}")
            print(f"Chunk ID: {chunk_id}")
            print(f"Hybrid score: {hybrid_score}")
            print(f"Reranker score: {reranker_score}")

            if (
                source == expected_source
                and chunk_id == expected_chunk_id
            ):
                if found_rank is None:
                    found_rank = rank

        if found_rank is not None:

            retrieval_hits += 1

            if found_rank == 1:
                hit_at_1 += 1

            if found_rank <= 3:
                hit_at_3 += 1

            if found_rank <= 5:
                hit_at_5 += 1

            reciprocal_rank_sum += 1.0 / found_rank

            print("\nCorrect chunk retrieved.")
            print(f"Correct rank: {found_rank}")
            print("Retrieval: PASS")

        else:

            print("\nCorrect chunk was not retrieved.")
            print("Retrieval: FAIL")

            print("Hit@1: FAIL")
            print("Hit@3: FAIL")
            print("Hit@5: FAIL")
            print("Reciprocal Rank: 0.0000")

            continue

        print(
            f"Hit@1: {'PASS' if found_rank <= 1 else 'FAIL'}"
        )

        print(
            f"Hit@3: {'PASS' if found_rank <= 3 else 'FAIL'}"
        )

        print(
            f"Hit@5: {'PASS' if found_rank <= 5 else 'FAIL'}"
        )

        print(
            f"Reciprocal Rank: {1.0 / found_rank:.4f}"
        )

    # ==========================================
    # Metrics
    # ==========================================

    hit_rate = retrieval_hits / total_questions
    hit_at_1_rate = hit_at_1 / total_questions
    hit_at_3_rate = hit_at_3 / total_questions
    hit_at_5_rate = hit_at_5 / total_questions
    mrr = reciprocal_rank_sum / total_questions

    print("\n")
    print("=" * 70)
    print("RAG Evaluation Summary")
    print("=" * 70)

    print(f"Questions evaluated: {total_questions}")
    print(f"Retrieval hits: {retrieval_hits}")
    print(f"Retrieval Hit Rate: {hit_rate:.2%}")
    print(f"Hit@1: {hit_at_1_rate:.2%}")
    print(f"Hit@3: {hit_at_3_rate:.2%}")
    print(f"Hit@5: {hit_at_5_rate:.2%}")
    print(f"MRR: {mrr:.4f}")

    print("=" * 70)


# ==========================================
# Main
# ==========================================

if __name__ == "__main__":
    evaluate()
