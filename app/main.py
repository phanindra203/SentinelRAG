from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="SentinelRAG")


class QueryRequest(BaseModel):
    question: str


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/query")
def query(request: QueryRequest):
    return {
        "question": request.question,
        "answer": "This is a placeholder response."
    }

