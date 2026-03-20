"""Handler for /start command."""


def handle_start(args: str = "") -> str:
    """Handle the /start command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        Welcome message text.
    """
    return (
        "👋 Welcome to the SE Toolkit Bot!\n\n"
        "I can help you check your lab scores, view available labs, "
        "and get assistance with your software engineering coursework.\n\n"
        "Use /help to see available commands."
    )
