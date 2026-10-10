import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI
from pydantic import BaseModel

from app.retriever import search_documents


load_dotenv()


# =========================
# FastAPI application
# =========================

app = FastAPI(title="SentinelRAG")


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
    question: str


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
def query(request: QueryRequest):

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
