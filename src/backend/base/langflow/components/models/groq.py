from langchain_groq import ChatGroq
from pydantic.v1 import SecretStr

from langflow.base.models.groq_constants import GROQ_MODELS
from langflow.base.models.model import LCModelComponent
from langflow.field_typing import LanguageModel
from langflow.inputs.inputs import HandleInput
from langflow.io import DropdownInput, FloatInput, IntInput, MessageTextInput, SecretStrInput


class GroqModel(LCModelComponent):
    display_name: str = "Groq"
    description: str = "Generate text using Groq."
    icon = "Groq"
    name = "GroqModel"

    inputs = [
        *LCModelComponent._base_inputs,
        SecretStrInput(name="groq_api_key", display_name="Groq API Key", info="API key for the Groq API."),
        MessageTextInput(
            name="groq_api_base",
            display_name="Groq API Base",
            info="Base URL path for API requests, leave blank if not using a proxy or service emulator.",
            advanced=True,
            value="https://api.groq.com",
        ),
        IntInput(
            name="max_tokens",
            display_name="Max Output Tokens",
            info="The maximum number of tokens to generate.",
            advanced=True,
        ),
        FloatInput(
            name="temperature",
            display_name="Temperature",
            info="Run inference with this temperature. Must by in the closed interval [0.0, 1.0].",
            value=0.1,
        ),
        IntInput(
            name="n",
            display_name="N",
            info="Number of chat completions to generate for each prompt. "
            "Note that the API may not return the full n completions if duplicates are generated.",
            advanced=True,
        ),
        DropdownInput(
            name="model_name",
            display_name="Model",
            info="The name of the model to use.",
            options=GROQ_MODELS,
            value="llama-3.1-8b-instant",
        ),
        HandleInput(
            name="output_parser",
            display_name="Output Parser",
            info="The parser to use to parse the output of the model",
            advanced=True,
            input_types=["OutputParser"],
        ),
    ]

    def build_model(self) -> LanguageModel:  # type: ignore[type-var]
        groq_api_key = self.groq_api_key
        model_name = self.model_name
        max_tokens = self.max_tokens
        temperature = self.temperature
        groq_api_base = self.groq_api_base
        n = self.n
        stream = self.stream

        return ChatGroq(
            model=model_name,
            max_tokens=max_tokens or None,
            temperature=temperature,
            base_url=groq_api_base,
            n=n or 1,
            api_key=SecretStr(groq_api_key).get_secret_value(),
            streaming=stream,
        )
