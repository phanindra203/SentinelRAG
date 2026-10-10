from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

credential = DefaultAzureCredential()

token = credential.get_token(
    "https://cognitiveservices.azure.com/.default"
)

client = AzureOpenAI(
    azure_endpoint="https://sentinelrag-ai-boundary.cognitiveservices.azure.com/",
    api_version="2024-10-21",
    azure_ad_token=token.token,
)

response = client.embeddings.create(
    model="text-embedding-3-small",
    input="Terraform remote state stores infrastructure state centrally.",
)

print("Embedding created successfully")
print("Dimensions:", len(response.data[0].embedding))
