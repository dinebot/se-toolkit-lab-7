"""LLM client for natural language intent routing."""

import httpx


class LLMClient:
    """Client for interacting with LLM services for intent detection."""

    def __init__(self, api_key: str):
        """Initialize the LLM client.
        
        Args:
            api_key: API key for the LLM service.
        """
        self.api_key = api_key

    async def detect_intent(self, message: str) -> str:
        """Detect the intent from a user message.
        
        Args:
            message: The user's message text.
            
        Returns:
            Detected intent (e.g., 'start', 'help', 'health', 'labs', 'scores').
        """
        # TODO: Implement actual LLM call for intent detection
        # For now, return a default intent
        return "unknown"
