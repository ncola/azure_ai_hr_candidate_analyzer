from dotenv import load_dotenv
import os
from openai import AzureOpenAI

load_dotenv()

class AzureOpenAIClient:
    """
    Klient do komunikacji z Azure OpenAI
    """

    def __init__(self):
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
        self.api_version = os.getenv("API_VERSION")

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version
        )

    def ask_question(self, input):
        response = self.client.responses.create(   
            model=self.deployment, 
            input=str(input),
            )
        return response.model_dump_json(indent=2)
