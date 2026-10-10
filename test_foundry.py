import os

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

load_dotenv()

project = AIProjectClient(
    endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

client = project.get_openai_client()

response = client.responses.create(
    model=os.environ["FOUNDRY_MODEL_DEPLOYMENT"],
    input="Explain Kubernetes HPA in 3 simple sentences.",
)

print(response.output_text)
