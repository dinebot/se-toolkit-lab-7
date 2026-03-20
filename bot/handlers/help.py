"""Handler for /help command."""


def handle_help(args: str = "") -> str:
    """Handle the /help command.
    
    Args:
        args: Optional arguments passed with the command.
        
    Returns:
        List of available commands.
    """
    return (
        "📚 Available Commands:\n\n"
        "/start - Welcome message\n"
        "/help - Show this help message\n"
        "/health - Check backend service status\n"
        "/labs - List available labs\n"
        "/scores <lab-id> - Get your scores for a specific lab\n\n"
        "You can also ask questions like 'what labs are available?'"
    )
