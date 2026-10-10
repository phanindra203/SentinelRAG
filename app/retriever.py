import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from openai import OpenAI


load_dotenv()


# =========================
# Azure configuration
# =========================

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
INDEX_NAME = "sentinelrag-index"

FOUNDRY_OPENAI_ENDPOINT = (
    "https://sentinelrag-ai-boundary.openai.azure.com/openai/v1/"
)

EMBEDDING_DEPLOYMENT = "text-embedding-3-small"


# =========================
# Azure authentication
# =========================

credential = DefaultAzureCredential()

token_provider = get_bearer_token_provider(
    credential,
    "https://cognitiveservices.azure.com/.default",
)


# =========================
# Azure OpenAI client
# =========================

openai_client = OpenAI(
    base_url=FOUNDRY_OPENAI_ENDPOINT,
    api_key=token_provider,
)


# =========================
# Azure AI Search client
# =========================

search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=credential,
)


# =========================
# Generate query embedding
# =========================

def generate_query_embedding(question: str):

    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=question,
    )

    return response.data[0].embedding


# =========================
# Hybrid Search + Reranking
# =========================

def search_documents(
    question: str,
    top_k: int = 5,
    reranker_threshold: float = 2.0,
):

    print(f"Query: {question}")

    # Generate embedding for the user question
    query_vector = generate_query_embedding(question)

    print(
        f"Query embedding generated: "
        f"{len(query_vector)} dimensions"
    )

    # =========================
    # Vector search
    # =========================

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="contentVector",
        kind="vector",
    )

    # =========================
    # Hybrid search
    # Keyword + Vector
    # =========================

    results = search_client.search(
        search_text=question,
        vector_queries=[vector_query],
        select=[
            "id",
            "filename",
            "content",
        ],
        query_type="semantic",
        semantic_configuration_name="sentinelrag-semantic-config",
        top=top_k,
    )

    # =========================
    # Process and filter results
    # =========================

    documents = []

    for result in results:

        reranker_score = result.get(
            "@search.reranker_score"
        )

        # Ignore results below our initial
        # semantic relevance threshold.
        if (
            reranker_score is not None
            and reranker_score < reranker_threshold
        ):
            continue

        documents.append({
            "id": result["id"],
            "filename": result["filename"],
            "content": result["content"],
            "score": result["@search.score"],
            "reranker_score": reranker_score,
        })

    return documents


# =========================
# Local test
# =========================

if __name__ == "__main__":

    question = "What is a Kubernetes Deployment?"

    results = search_documents(
        question,
        top_k=5,
    )

    print("\nRetrieved documents:\n")

    for result in results:

        print("=" * 60)

        print(
            f"Filename: {result['filename']}"
        )

        print(
            f"Hybrid score: {result['score']}"
        )

        print(
            f"Reranker score: "
            f"{result['reranker_score']}"
        )

        print("=" * 60)

        print(result["content"])

        print()
