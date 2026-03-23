"""Handler for /health command."""

import asyncio
from services.lms_client import LMSClient


def handle_health(args: str = "", lms_client: LMSClient = None) -> str:
    """Handle the /health command.

    Args:
        args: Optional arguments passed with the command.
        lms_client: Optional LMS client instance for testing.

    Returns:
        Backend service status.
    """
    return asyncio.run(_handle_health_async(lms_client))


async def _handle_health_async(lms_client: LMSClient = None) -> str:
    """Async implementation of health handler."""
    if lms_client is None:
        from config import load_config
        config = load_config()
        lms_client = LMSClient(
            base_url=config["LMS_API_URL"],
            api_key=config["LMS_API_KEY"],
        )
        should_close = True
    else:
        should_close = False

    try:
        health = await lms_client.get_health()
        return (
            f"🏥 Health Status:\n\n"
            f"Backend: OK\n"
            f"Items in database: {health['items_count']}\n\n"
            f"All systems operational!"
        )
    except Exception as e:
        return (
            f"🏥 Health Status:\n\n"
            f"Backend: DOWN\n"
            f"Error: {str(e)}\n\n"
            f"The backend service is currently unavailable."
        )
    finally:
        if should_close:
            await lms_client.close()
