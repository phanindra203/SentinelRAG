def generate_answer(question: str, context: str) -> str:
    prompt = f"""
Answer the question using only the context provided below.

Context:
{context}

Question:
{question}
"""

    return prompt
