import os

from typing import List

from langflow.custom import Component
from langflow.io import FileInput, SecretStrInput, Output
from langflow.schema import Data
from langchain_unstructured import UnstructuredLoader


class UnstructuredComponent(Component):
    display_name = "Unstructured"
    description = "Unstructured data loader"
    documentation = "https://python.langchain.com/v0.2/docs/integrations/providers/unstructured/"
    trace_type = "tool"
    icon = "Unstructured"
    name = "Unstructured"

    inputs = [
        FileInput(
            name="file",
            display_name="File",
            required=True,
            info="The path to the file with which you want to use Unstructured to parse",
            file_types=[".pdf", ".docx"],  # TODO: Support all unstructured file types
        ),
        SecretStrInput(
            name="api_key",
            display_name="API Key",
            required=False,
            info="Unstructured API Key. Create at: https://unstructured.io/ - If not provided, open source library will be used",
        ),
    ]

    outputs = [
        Output(name="data", display_name="Data", method="load_documents"),
    ]

    def build_unstructured(self) -> UnstructuredLoader:
        os.environ["UNSTRUCTURED_API_KEY"] = self.api_key

        file_paths = [self.file]

        loader = UnstructuredLoader(file_paths)

        return loader

    def load_documents(self) -> List[Data]:
        unstructured = self.build_unstructured()

        documents = unstructured.load()
        data = [Data.from_document(doc) for doc in documents]  # Using the from_document method of Data

        self.status = data

        return data
