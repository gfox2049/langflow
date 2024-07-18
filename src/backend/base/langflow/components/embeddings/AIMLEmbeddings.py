from typing import Any
from langflow.base.embeddings.model import LCEmbeddingsModel
from langflow.base.models.aiml_constants import EMBEDDING_MODELS
from langflow.components.embeddings.util.AIMLEmbeddingsImpl import AIMLEmbeddingsImpl
from langflow.field_typing import Embeddings
from langflow.inputs.inputs import DropdownInput
from langflow.io import SecretStrInput


class AIMLEmbeddingsComponent(LCEmbeddingsModel):
    display_name = "AI/ML Embeddings"
    description = "Generate embeddings using the AI/ML API."
    icon = "OpenAI"  # TODO: icon
    name = "AIMLEmbeddings"

    inputs = [
        DropdownInput(
            name="model_name",
            display_name="Model Name",
            options=EMBEDDING_MODELS,
            required=True,
        ),
        SecretStrInput(
            name="aiml_api_key",
            display_name="AI/ML API Key",
            value="AIML_API_KEY",
            required=True,
        ),
    ]

    def build_embeddings(self) -> Embeddings:
        return AIMLEmbeddingsImpl(
            api_key=self.aiml_api_key,
            model=self.model_name,
        )
