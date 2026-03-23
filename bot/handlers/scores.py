"""Handler for /scores command."""

import asyncio
from services.lms_client import LMSClient


def handle_scores(lab_id: str = "", lms_client: LMSClient = None) -> str:
    """Handle the /scores command.

    Args:
        lab_id: The lab identifier to get scores for.
        lms_client: Optional LMS client instance for testing.

    Returns:
        Score information for the specified lab.
    """
    return asyncio.run(_handle_scores_async(lab_id, lms_client))


async def _handle_scores_async(lab_id: str = "", lms_client: LMSClient = None) -> str:
    """Async implementation of scores handler."""
    if not lab_id:
        return "Please specify a lab ID. Example: /scores lab-04"

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
        scores = await lms_client.get_scores(lab_id)
        if not scores:
            return f"📊 Scores for {lab_id}:\n\nNo data found for this lab."

        # Format each task's scores
        score_lines = []
        for task in scores:
            task_name = task.get("task", "Unknown task")
            avg_score = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            score_lines.append(f"• {task_name}: {avg_score:.1f}% ({attempts} attempts)")

        return (
            f"📊 Scores for {lab_id}:\n\n"
            + "\n".join(score_lines)
        )
    except Exception as e:
        return (
            f"📊 Scores for {lab_id}:\n\n"
            f"Error fetching scores: {str(e)}\n\n"
            "The backend service is currently unavailable."
        )
    finally:
        if should_close:
            await lms_client.close()
