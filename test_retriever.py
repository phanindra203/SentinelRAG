from app.retriever import search_documents


results = search_documents(
    "How does Terraform remote state work?"
)

for result in results:
    print("=" * 60)
    print("DOCUMENT:", result["filename"])
    print("SCORE:", result["score"])
    print(result["content"])
