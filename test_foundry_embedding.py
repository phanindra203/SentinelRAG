import os

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

credential = DefaultAzureCredential()

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=credential,
)

openai_client = project.get_openai_client()

response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input="Terraform remote state stores infrastructure state centrally.",
)

print("Embedding created successfully")
print("Dimensions:", len(response.data[0].embedding))
