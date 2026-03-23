"""LMS API client for fetching scores and lab data."""

import httpx


class LMSClient:
    """Client for interacting with the LMS API."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.

        Args:
            base_url: Base URL of the LMS API.
            api_key: API key for authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    async def get_scores(self, lab_id: str) -> list:
        """Fetch pass rates for a specific lab.

        Args:
            lab_id: The lab identifier (e.g., 'lab-04').

        Returns:
            List of task pass rate dictionaries with 'task', 'avg_score', 'attempts'.
        """
        response = await self._client.get(
            "/analytics/pass-rates",
            params={"lab": lab_id},
        )
        response.raise_for_status()
        return response.json()

    async def get_labs(self) -> list:
        """Fetch list of available labs from the backend.

        Returns:
            List of lab dictionaries with 'id', 'title', 'type'.
        """
        response = await self._client.get("/items/")
        response.raise_for_status()
        items = response.json()
        # Filter to only top-level labs (type='lab', parent_id=None)
        return [item for item in items if item.get("type") == "lab" and item.get("parent_id") is None]

    async def get_health(self) -> dict:
        """Check backend health by fetching items count.

        Returns:
            Dict with 'status' and 'items_count'.
        """
        response = await self._client.get("/items/")
        response.raise_for_status()
        items = response.json()
        return {"status": "ok", "items_count": len(items)}

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
