import pytest
from fastapi import status
from httpx import AsyncClient


async def test_create_flow(client: AsyncClient, logged_in_headers):
    basic_case = {
        "name": "string",
        "description": "string",
        "icon": "string",
        "icon_bg_color": "#ff00ff",
        "gradient": "string",
        "data": {},
        "is_component": False,
        "webhook": False,
        "endpoint_name": "string",
        "tags": [
            "string"
        ],
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "folder_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    }
    response = await client.post("api/v1/flows/", json=basic_case, headers=logged_in_headers)
    result = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert isinstance(result, dict), "The result must be a dictionary"
    assert "data" in result.keys(), "The result must have a 'data' key"
    assert "description" in result.keys(), "The result must have a 'description' key"
    assert "endpoint_name" in result.keys(), "The result must have a 'endpoint_name' key"
    assert "folder_id" in result.keys(), "The result must have a 'folder_id' key"
    assert "gradient" in result.keys(), "The result must have a 'gradient' key"
    assert "icon" in result.keys(), "The result must have a 'icon' key"
    assert "icon_bg_color" in result.keys(), "The result must have a 'icon_bg_color' key"
    assert "id" in result.keys(), "The result must have a 'id' key"
    assert "is_component" in result.keys(), "The result must have a 'is_component' key"
    assert "name" in result.keys(), "The result must have a 'name' key"
    assert "tags" in result.keys(), "The result must have a 'tags' key"
    assert "updated_at" in result.keys(), "The result must have a 'updated_at' key"
    assert "user_id" in result.keys(), "The result must have a 'user_id' key"
    assert "webhook" in result.keys(), "The result must have a 'webhook' key"
