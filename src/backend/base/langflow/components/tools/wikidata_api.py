from typing import Any
import httpx
from langflow.custom import Component
from langflow.helpers.data import data_to_text
from langflow.io import Output, MultilineInput
from langflow.schema import Data
from langflow.schema.message import Message


class WikidataComponent(Component):
    display_name = "Wikidata API"
    description = "Performs a search using the Wikidata API."
    name = "WikidataAPI"
    icon = "Wikipedia"

    inputs = [
        MultilineInput(
            name="query",
            display_name="Query",
            info="The text query for similarity search on Wikidata.",
            required=True,
            tool_mode=True,
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="fetch_content"),
        Output(display_name="Text", name="text", method="fetch_content_text"),
    ]

    def fetch_content(self) -> list[Data]:
        try:
            # Define request parameters for Wikidata API
            params = {
                "action": "wbsearchentities",
                "format": "json",
                "search": self.query,
                "language": "en",
            }
            
            # Send request to Wikidata API
            wikidata_api_url = "https://www.wikidata.org/w/api.php"
            response = httpx.get(wikidata_api_url, params=params)
            response.raise_for_status()
            response_json = response.json()
            
            # Extract search results
            results = response_json.get("search", [])
            
            if not results:
                return [Data(data={"error": "No search results found for the given query."})]

            # Transform the API response into Data objects
            data = [
                Data(
                    text=f"{result['label']}: {result.get('description', '')}",
                    data={
                        "label": result["label"],
                        "id": result.get("id"),
                        "url": result.get("url"),
                        "description": result.get("description", ""),
                        "concepturi": result.get("concepturi"),
                    }
                )
                for result in results
            ]
            
            self.status = data
            return data

        except Exception as e:
            error_message = f"Error in Wikidata Search API: {str(e)}"
            return [Data(data={"error": error_message})]

    def fetch_content_text(self) -> Message:
        data = self.fetch_content()
        result_string = data_to_text("{text}", data)
        self.status = result_string
        return Message(text=result_string)