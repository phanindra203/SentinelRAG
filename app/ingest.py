import os
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import OpenAI
from azure.search.documents import SearchClient


# =========================
# Load environment variables
# =========================

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

KNOWLEDGE_DIR = Path("docs/knowledge")


# =========================
# Chunk configuration
# =========================

CHUNK_SIZE = 500


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
# Load knowledge documents
# =========================

def load_documents():

    documents = []

    for file_path in sorted(KNOWLEDGE_DIR.glob("*.md")):

        content = file_path.read_text(
            encoding="utf-8"
        )

        documents.append({
            "filename": file_path.name,
            "content": content,
        })

    return documents


# =========================
# Markdown / paragraph-aware
# chunking
# =========================

def chunk_text(text):

    # Split the document using blank lines.
    # This preserves paragraph boundaries.
    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []

    current_chunk = ""

    for paragraph in paragraphs:

        # Keep paragraphs together when possible.
        if (
            len(current_chunk)
            + len(paragraph)
            + 2
            <= CHUNK_SIZE
        ):

            if current_chunk:

                current_chunk += "\n\n"

            current_chunk += paragraph

        else:

            # Save the current chunk.
            if current_chunk:

                chunks.append(
                    current_chunk
                )

            # Start a new chunk.
            current_chunk = paragraph

    # Save the final chunk.
    if current_chunk:

        chunks.append(
            current_chunk
        )

    return chunks

# =========================
# Generate embedding
# =========================

def generate_embedding(text):

    response = openai_client.embeddings.create(
        model=EMBEDDING_DEPLOYMENT,
        input=text,
    )

    return response.data[0].embedding


# =========================
# Ingest documents
# =========================

def ingest_documents():

    documents = load_documents()

    search_documents = []

    document_id = 1

    for document in documents:

        print()
        print(
            f"Processing: "
            f"{document['filename']}"
        )

        # Create logical chunks.
        chunks = chunk_text(
            document["content"]
        )

        print(
            f"Chunks created: "
            f"{len(chunks)}"
        )

        for chunk_number, chunk in enumerate(
            chunks,
            start=1
        ):

            print()
            print(
                f"Chunk {chunk_number}/"
                f"{len(chunks)}"
            )

            print("-" * 60)

            print(chunk)

            print("-" * 60)

            # Generate embedding.
            embedding = generate_embedding(
                chunk
            )

            print(
                f"Embedding generated: "
                f"{len(embedding)} dimensions"
            )

            # Prepare Azure AI Search document.
            search_documents.append({

                "id": str(document_id),

                "filename": document["filename"],

                "content": chunk,

                "contentVector": embedding,
            })

            document_id += 1

    # =========================
    # Upload to Azure AI Search
    # =========================

    print()
    print(
        f"Total chunks to upload: "
        f"{len(search_documents)}"
    )

    print()

    print(
        "Uploading chunks to "
        "Azure AI Search..."
    )

    result = search_client.upload_documents(
        documents=search_documents
    )

    print()

    print(
        "Upload complete."
    )

    # =========================
    # Upload results
    # =========================

    for item in result:

        print(
            f"Key: {item.key}, "
            f"Succeeded: {item.succeeded}, "
            f"Error: {item.error_message}"
        )


# =========================
# Application entry point
# =========================

if __name__ == "__main__":

    ingest_documents()
