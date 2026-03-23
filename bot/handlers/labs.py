"""Handler for /labs command."""

import asyncio
from services.lms_client import LMSClient


def handle_labs(args: str = "", lms_client: LMSClient = None) -> str:
    """Handle the /labs command.

    Args:
        args: Optional arguments passed with the command.
        lms_client: Optional LMS client instance for testing.

    Returns:
        List of available labs.
    """
    return asyncio.run(_handle_labs_async(lms_client))


async def _handle_labs_async(lms_client: LMSClient = None) -> str:
    """Async implementation of labs handler."""
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
        labs = await lms_client.get_labs()
        if not labs:
            return "📋 Available Labs:\n\nNo labs found."

        lab_lines = []
        for lab in labs:
            lab_id = lab.get("id", "")
            title = lab.get("title", "Unknown")
            lab_lines.append(f"• {title}")

        return (
            "📋 Available Labs:\n\n"
            + "\n".join(lab_lines)
            + "\n\nUse /scores <lab-id> to check your scores."
        )
    except Exception as e:
        return (
            "📋 Available Labs:\n\n"
            f"Error fetching labs: {str(e)}\n\n"
            "The backend service is currently unavailable."
        )
    finally:
        if should_close:
            await lms_client.close()
