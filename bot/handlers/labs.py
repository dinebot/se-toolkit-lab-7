"""Handler for /labs command."""


def handle_labs(args: str = "") -> str:
    """Handle the /labs command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        List of available labs.
    """
    # TODO: Fetch actual labs from backend
    return (
        "📋 Available Labs:\n\n"
        "• Lab 4 - Security Toolkit Introduction\n"
        "• Lab 5 - Web Application Security\n"
        "• Lab 6 - Network Security\n"
        "• Lab 7 - Social Engineering Defense\n\n"
        "Use /scores <lab-id> to check your scores."
    )
