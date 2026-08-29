"""Homebox API Client module.

This module provides the HomeboxClient class which encapsulates
interactions with the Homebox API.
"""

import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class HomeboxClient:
    """HomeboxClient provides an interface to interact with the Homebox API.

    Design Pattern: Client/Gateway Pattern (SOLID single responsibility for API interactions).
    """

    def __init__(self, url: str, token: str) -> None:
        """Initialize the HomeboxClient.

        Args:
            url (str): The base URL of the Homebox API.
            token (str): The authorization bearer token.
        """
        self.url = url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def get_items_by_tag(self, tag: str) -> list[dict[str, Any]]:
        """Fetch items filtered by a specific tag.

        Args:
            tag (str): The tag to filter by.

        Returns:
            list[dict[str, Any]]: A list of items (entities) that have the given tag.

        Raises:
            RuntimeError: If the API request fails.
        """
        endpoint = f"{self.url}/api/v1/entities"
        params = {"tags": [tag]}
        try:
            response = requests.get(endpoint, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch items by tag {tag}") from e

    def get_item(self, item_id: str) -> dict[str, Any]:
        """Fetch a specific item by its ID.

        Args:
            item_id (str): The ID of the item.

        Returns:
            dict[str, Any]: The item data.

        Raises:
            RuntimeError: If the API request fails.
        """
        endpoint = f"{self.url}/api/v1/entities/{item_id}"
        try:
            response = requests.get(endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch item {item_id}") from e

    def update_item_tags(self, item_id: str, tags_to_add: list[str], tags_to_remove: list[str]) -> dict[str, Any]:
        """Update the tags of a specific item.

        Args:
            item_id (str): The ID of the item to update.
            tags_to_add (list[str]): A list of tag strings to add.
            tags_to_remove (list[str]): A list of tag strings to remove.

        Returns:
            dict[str, Any]: The updated item data.

        Raises:
            RuntimeError: If the API request fails.
        """
        item = self.get_item(item_id)
        current_tags = item.get("tags", [])

        # Remove tags based on string name or id in dict
        new_tags = []
        for tag in current_tags:
            tag_name = tag.get("name") if isinstance(tag, dict) else tag
            tag_id = tag.get("id") if isinstance(tag, dict) else tag
            if tag_name not in tags_to_remove and tag_id not in tags_to_remove:
                new_tags.append(tag)

        # Add new tags
        existing_names = {t.get("name") if isinstance(t, dict) else t for t in new_tags}
        for t_add in tags_to_add:
            if t_add not in existing_names:
                new_tags.append({"name": t_add})

        item["tags"] = new_tags

        endpoint = f"{self.url}/api/v1/entities/{item_id}"
        try:
            response = requests.put(endpoint, headers=self.headers, json=item, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to update item {item_id}") from e
