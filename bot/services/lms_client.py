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

    async def get_scores(self, lab_id: str) -> dict:
        """Fetch scores for a specific lab.
        
        Args:
            lab_id: The lab identifier.
            
        Returns:
            Score data dictionary.
        """
        # TODO: Implement actual API call
        return {"lab_id": lab_id, "score": None, "status": "pending"}

    async def get_labs(self) -> list:
        """Fetch list of available labs.
        
        Returns:
            List of lab dictionaries.
        """
        # TODO: Implement actual API call
        return []

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()
