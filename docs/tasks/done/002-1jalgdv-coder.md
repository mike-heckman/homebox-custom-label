# Task 2: Setup Homebox API Client

## Context
The scan mode requires reading items by tag and updating their tags via a read-modify-write process using the Homebox API.

## Implementation Plan
1. Create `src/homebox_api.py`.
2. Create a `HomeboxClient` class initialized with URL and Token.
3. Implement `get_items_by_tag(tag: str)` referring to the `docs/reference/homebox-api` for the correct endpoint (likely `/api/v1/items?tags={tag}`).
4. Implement `update_item_tags(item_id: str, tags_to_add: list[str], tags_to_remove: list[str])`.
   - First `GET` the item to read current tags.
   - Modify the tags array.
   - `PUT` or `PATCH` the item with the updated tags.
5. Create `tests/test_homebox_api.py` mocking `requests` and ensuring standard read-modify-write payload logic is solid.

## Success Criteria
- [x] Client can correctly fetch items by tag.
- [x] Client can correctly update an item's tags without overwriting other properties.
- [x] Unit tests pass with >= 80% coverage.
