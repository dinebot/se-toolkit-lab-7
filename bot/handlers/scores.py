"""Handler for /scores command."""


def handle_scores(lab_id: str = "") -> str:
    """Handle the /scores command.
    
    Args:
        lab_id: The lab identifier to get scores for.
        
    Returns:
        Score information for the specified lab.
    """
    if not lab_id:
        return "Please specify a lab ID. Example: /scores lab-04"
    
    # TODO: Fetch actual scores from backend
    return (
        f"📊 Scores for {lab_id}:\n\n"
        f"Status: Pending (placeholder)\n"
        "Score: --\n\n"
        "Check back later for updated scores."
    )
