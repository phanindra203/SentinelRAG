import logging
import time
import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.retriever import search_documents


load_dotenv()


# =========================
# FastAPI application
# =========================

app = FastAPI(title="SentinelRAG")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinelrag")

REQUEST_COUNT = Counter(
    "sentinelrag_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "sentinelrag_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        logger.exception(
            "request failed method=%s path=%s",
            request.method,
            request.url.path,
        )
        raise
    finally:
        duration_seconds = time.perf_counter() - start_time
        duration_ms = duration_seconds * 1000

        REQUEST_COUNT.labels(
            request.method, request.url.path, str(status_code)
        ).inc()
        REQUEST_DURATION.labels(
            request.method, request.url.path
        ).observe(duration_seconds)

        logger.info(
            "request method=%s path=%s status=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            status_code,
            duration_ms,
        )



@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str | None = Security(api_key_header)):
    expected_key = os.environ.get("SENTINELRAG_API_KEY")
    if not expected_key or not api_key or api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# =========================
# Microsoft Foundry client
# =========================

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

client = project.get_openai_client()


# =========================
# Request model
# =========================

class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)



# =========================
# Health check
# =========================

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


# =========================
# RAG Query Endpoint
# =========================

@app.post("/query")
def query(
    request: QueryRequest,
    _: None = Depends(verify_api_key),
):

    # Retrieve relevant chunks
    results = search_documents(
        request.question,
        top_k=5,
    )

    # No relevant documents
    if not results:
        return {
            "question": request.question,
            "answer": (
                "I could not find enough relevant information "
                "in the knowledge base to answer this question."
            ),
            "sources": [],
        }

    # Build retrieved context
    context_parts = []

    for result in results:

        context_parts.append(
            f"""
Source: {result["filename"]}
Chunk ID: {result["id"]}
Hybrid Score: {result["score"]}
Semantic Reranker Score: {result["reranker_score"]}

Content:
{result["content"]}
"""
        )

    context = "\n\n".join(context_parts)

    # Grounded RAG prompt
    prompt = f"""
You are SentinelRAG, a retrieval-augmented AI assistant.

Answer the user's question using ONLY the information
contained in the retrieved context below.

Rules:

1. Do not invent facts.
2. Do not use knowledge outside the retrieved context.
3. If the context does not contain enough information,
   clearly state that the information is not available
   in the knowledge base.
4. Give a concise and technically accurate answer.
5. When appropriate, mention the source document.

Retrieved Context:

{context}

User Question:

{request.question}
"""

    # Generate answer using Microsoft Foundry
    response = client.responses.create(
        model=os.environ["FOUNDRY_MODEL_DEPLOYMENT"],
        input=prompt,
    )

    # Return answer + retrieval metadata
    return {
        "question": request.question,
        "answer": response.output_text,
        "sources": [
            {
                "id": result["id"],
                "filename": result["filename"],
                "hybrid_score": result["score"],
                "reranker_score": result["reranker_score"],
            }
            for result in results
        ],
    }
