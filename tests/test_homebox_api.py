from unittest.mock import MagicMock

import pytest
import requests

from src.homebox_api import HomeboxClient


@pytest.fixture
def client() -> HomeboxClient:
    """Fixture providing a configured HomeboxClient."""
    return HomeboxClient("http://mock-homebox", "mock-token")


def test_get_items_by_tag(mocker: MagicMock, client: HomeboxClient) -> None:
    """Test fetching items by a tag successfully."""
    mock_get = mocker.patch("requests.get")
    mock_response = MagicMock()
    mock_response.json.return_value = {"items": [{"id": "item1"}, {"id": "item2"}]}
    mock_get.return_value = mock_response

    items = client.get_items_by_tag("my-tag")

    mock_get.assert_called_once_with(
        "http://mock-homebox/api/v1/entities",
        headers={"Authorization": "Bearer mock-token", "Content-Type": "application/json"},
        params={"tags": ["my-tag"]},
        timeout=10,
    )
    assert items == [{"id": "item1"}, {"id": "item2"}]


def test_get_items_by_tag_error(mocker: MagicMock, client: HomeboxClient) -> None:
    """Test fetching items by tag handles HTTP errors."""
    mock_get = mocker.patch("requests.get")
    mock_get.side_effect = requests.RequestException("HTTP Error")

    with pytest.raises(RuntimeError, match="Failed to fetch items by tag error-tag"):
        client.get_items_by_tag("error-tag")


def test_get_item(mocker: MagicMock, client: HomeboxClient) -> None:
    """Test fetching a specific item by ID."""
    mock_get = mocker.patch("requests.get")
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "item123", "name": "Tool"}
    mock_get.return_value = mock_response

    item = client.get_item("item123")

    mock_get.assert_called_once_with(
        "http://mock-homebox/api/v1/entities/item123",
        headers={"Authorization": "Bearer mock-token", "Content-Type": "application/json"},
        timeout=10,
    )
    assert item["name"] == "Tool"


def test_update_item_tags(mocker: MagicMock, client: HomeboxClient) -> None:
    """Test read-modify-write process for updating an item's tags."""
    # Mock GET
    mock_get = mocker.patch.object(client, "get_item")
    mock_get.return_value = {
        "id": "item1",
        "name": "Widget",
        "tags": [{"id": "t1", "name": "keep-tag"}, {"id": "t2", "name": "remove-tag"}],
    }

    # Mock PUT
    mock_put = mocker.patch("requests.put")
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "item1", "tags": [{"name": "keep-tag"}, {"name": "new-tag"}]}
    mock_put.return_value = mock_response

    updated_item = client.update_item_tags("item1", tags_to_add=["new-tag"], tags_to_remove=["remove-tag"])

    # Ensure PUT was called correctly with the new tag array
    expected_payload = {
        "id": "item1",
        "name": "Widget",
        "tags": [{"id": "t1", "name": "keep-tag"}, {"name": "new-tag"}],
    }
    mock_put.assert_called_once_with(
        "http://mock-homebox/api/v1/entities/item1",
        headers={"Authorization": "Bearer mock-token", "Content-Type": "application/json"},
        json=expected_payload,
        timeout=10,
    )
    assert updated_item["id"] == "item1"


def test_update_item_tags_error(mocker: MagicMock, client: HomeboxClient) -> None:
    """Test update fails correctly on PUT error."""
    mocker.patch.object(client, "get_item", return_value={"id": "item2", "tags": []})
    mock_put = mocker.patch("requests.put")
    mock_put.side_effect = requests.RequestException("PUT error")

    with pytest.raises(RuntimeError, match="Failed to update item item2"):
        client.update_item_tags("item2", tags_to_add=["some-tag"], tags_to_remove=[])
