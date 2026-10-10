import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)

load_dotenv()

# =========================
# Azure configuration
# =========================

SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
INDEX_NAME = "sentinelrag-index"

# =========================
# Azure authentication
# =========================

credential = DefaultAzureCredential()

index_client = SearchIndexClient(
    endpoint=SEARCH_ENDPOINT,
    credential=credential,
)

# =========================
# Search index fields
# =========================


fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
    ),

    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
    ),

    SimpleField(
        name="filename",
        type=SearchFieldDataType.String,
        filterable=True,
    ),

    SearchField(
        name="contentVector",
        type=SearchFieldDataType.Collection(
            SearchFieldDataType.Single
        ),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_profile_name="sentinelrag-vector-profile",
    ),
]

# =========================
# Vector search configuration
# =========================

vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="sentinelrag-hnsw"
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="sentinelrag-vector-profile",
            algorithm_configuration_name="sentinelrag-hnsw",
        )
    ],
)

# =========================
# Semantic search configuration
# =========================

semantic_config = SemanticConfiguration(
    name="sentinelrag-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[
            SemanticField(
                field_name="content"
            )
        ]
    ),
)

semantic_search = SemanticSearch(
    configurations=[
        semantic_config
    ],
    default_configuration_name="sentinelrag-semantic-config",
)

# =========================
# Create / update index
# =========================

index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    vector_search=vector_search,
    semantic_search=semantic_search,
)

result = index_client.create_or_update_index(index)

print(f"Index created: {result.name}")
