import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from app.retriever import search_documents


load_dotenv()


# ==========================================
# Microsoft Foundry client
# ==========================================

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

client = project.get_openai_client()


# ==========================================
# Generation Evaluation Dataset
# ==========================================

EVALUATION_DATASET = [
    {
        "question": "What is a Kubernetes Deployment?",
        "expected_keywords": [
            "replicated Pods",
            "running application instances",
        ],
    },
    {
        "question": "What is a Kubernetes Pod?",
        "expected_keywords": [
            "smallest deployable unit",
            "container",
        ],
    },
    {
        "question": "What does a Kubernetes Service provide?",
        "expected_keywords": [
            "stable network endpoint",
            "Pods",
        ],
    },
    {
        "question": "What is Terraform remote state?",
        "expected_keywords": [
            "state file",
            "remote backend",
        ],
    },
    {
        "question": "Why use Azure Blob Storage for Terraform state?",
        "expected_keywords": [
            "remote backend",
            "Terraform state",
        ],
    },
    {
        "question": "What is the typical Terraform workflow?",
        "expected_keywords": [
            "terraform init",
            "terraform validate",
            "terraform plan",
            "terraform apply",
        ],
    },
    {
        "question": "What is the architecture of an AKS cluster?",
        "expected_keywords": [
            "managed control plane",
            "node pools",
            "worker nodes",
        ],
    },
    {
        "question": "What is an AKS node pool?",
        "expected_keywords": [
            "group of Kubernetes nodes",
            "same configuration",
        ],
    },
    {
        "question": "How does AKS integrate with Azure Container Registry?",
        "expected_keywords": [
            "Azure Container Registry",
            "container images",
            "cluster identity",
        ],
    },
    {
        "question": "How does AKS use managed identities?",
        "expected_keywords": [
            "managed identities",
            "Azure resources",
            "long-lived credentials",
        ],
    },
]


# ==========================================
# Generate grounded answer
# ==========================================

def generate_answer(question, results):

    context_parts = []

    for result in results:

        context_parts.append(
            f"""
Source: {result["filename"]}
Chunk ID: {result["id"]}

Content:
{result["content"]}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are SentinelRAG, a retrieval-augmented AI assistant.

Answer the user's question using ONLY the information
contained in the retrieved context.

Rules:

1. Do not invent facts.
2. Do not use knowledge outside the retrieved context.
3. If the context does not contain enough information,
   clearly say that the information is not available.
4. Give a concise and technically accurate answer.
5. Mention the source document when appropriate.

Retrieved Context:

{context}

User Question:

{question}
"""

    response = client.responses.create(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT"],
        input=prompt,
    )

    return response.output_text


# ==========================================
# Evaluate generated answer
# ==========================================

def evaluate():

    total_questions = len(EVALUATION_DATASET)

    generation_passes = 0

    print("\n")
    print("=" * 70)
    print("SentinelRAG - Answer Generation Evaluation")
    print("=" * 70)

    for index, test_case in enumerate(
        EVALUATION_DATASET,
        start=1,
    ):

        question = test_case["question"]
        expected_keywords = test_case["expected_keywords"]

        print("\n")
        print("-" * 70)
        print(f"Test {index}/{total_questions}")
        print(f"Question: {question}")
        print("-" * 70)

        # ----------------------------------
        # Retrieve evidence
        # ----------------------------------

        results = search_documents(
            question,
            top_k=5,
        )

        if not results:

            print("Retrieval: FAIL")
            print("Generation: SKIPPED")
            continue

        # ----------------------------------
        # Build retrieved evidence
        # ----------------------------------

        retrieved_context = "\n".join(
            result["content"]
            for result in results
        )

        # ----------------------------------
        # Generate answer
        # ----------------------------------

        answer = generate_answer(
            question,
            results,
        )

        print("\nGenerated Answer:")
        print(answer)

        # ----------------------------------
        # Check expected concepts
        # ----------------------------------

        answer_lower = answer.lower()
        context_lower = retrieved_context.lower()

        matched_keywords = []
        missing_keywords = []

        for keyword in expected_keywords:

            if keyword.lower() in answer_lower:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        # ----------------------------------
        # Check whether expected concepts
        # exist in retrieved evidence
        # ----------------------------------

        unsupported_keywords = [
            keyword
            for keyword in matched_keywords
            if keyword.lower() not in context_lower
        ]

        print("\nExpected concepts:")
        print(expected_keywords)

        print("\nMatched in answer:")
        print(matched_keywords)

        if missing_keywords:

            print("\nMissing from answer:")
            print(missing_keywords)

        if unsupported_keywords:

            print(
                "\nWARNING - Concepts found in answer "
                "but not retrieved context:"
            )

            print(unsupported_keywords)

        # ----------------------------------
        # Basic generation evaluation
        # ----------------------------------

        if (
            len(missing_keywords) == 0
            and len(unsupported_keywords) == 0
        ):

            generation_passes += 1
            print("\nGeneration evaluation: PASS")

        else:

            print("\nGeneration evaluation: REVIEW")

    # ======================================
    # Final summary
    # ======================================

    generation_rate = (
        generation_passes / total_questions
    ) * 100

    print("\n")
    print("=" * 70)
    print("Generation Evaluation Summary")
    print("=" * 70)

    print(
        f"Questions evaluated: "
        f"{total_questions}"
    )

    print(
        f"Generation passes: "
        f"{generation_passes}"
    )

    print(
        f"Generation Pass Rate: "
        f"{generation_rate:.2f}%"
    )

    print("=" * 70)


# ==========================================
# Run evaluation
# ==========================================

if __name__ == "__main__":
    evaluate()
