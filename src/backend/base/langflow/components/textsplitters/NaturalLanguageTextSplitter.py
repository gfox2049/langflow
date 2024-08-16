from typing import Any

from langchain_text_splitters import NLTKTextSplitter, TextSplitter

from langflow.base.textsplitters.model import LCTextSplitterComponent
from langflow.inputs import DataInput, IntInput, MessageTextInput
from langflow.utils.util import unescape_string


class NaturalLanguageTextSplitterComponent(LCTextSplitterComponent):
    display_name = "Natural Language Text Splitter"
    description = "Split text based on natural language boundaries, optimized for a specified language."
    name = "NaturalLanguageTextSplitter"

    inputs = [
        IntInput(
            name="chunk_size",
            display_name="Chunk Size",
            info="The maximum number of characters in each chunk after splitting.",
            value=1000,
        ),
        IntInput(
            name="chunk_overlap",
            display_name="Chunk Overlap",
            info="The number of characters that overlap between consecutive chunks.",
            value=200,
        ),
        DataInput(
            name="data_input",
            display_name="Input",
            info="The text data to be split.",
            input_types=["Document", "Data"],
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info='The character(s) to use as a delimiter when splitting text.\nDefaults to "\\n\\n" if left empty.',
        ),
        MessageTextInput(
            name="language",
            display_name="Language",
            info='The language of the text. Default is "English". Supports multiple languages for better text boundary recognition.',
        ),
    ]

    def get_data_input(self) -> Any:
        return self.data_input

    def build_text_splitter(self) -> TextSplitter:
        if self.separator:
            separator = unescape_string(self.separator)
        else:
            separator = "\n\n"
        return NLTKTextSplitter(
            language=self.language.lower() if self.language else "english",
            separator=separator,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
