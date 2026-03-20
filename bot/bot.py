#!/usr/bin/env python3
"""SE Toolkit Bot - Entry point.

Usage:
    uv run bot.py              # Start Telegram bot
    uv run bot.py --test CMD   # Test mode: print response to stdout
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


# Command routing map
COMMAND_HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def route_command(command: str) -> str:
    """Route a command string to the appropriate handler.
    
    Args:
        command: The command string (e.g., "/start" or "/scores lab-04").
        
    Returns:
        Handler response text.
    """
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    if cmd in COMMAND_HANDLERS:
        return COMMAND_HANDLERS[cmd](args)
    
    # Handle natural language queries (Task 3: intent routing)
    # For now, return a helpful response
    return (
        "I'm not sure what you're asking. Try /help to see available commands, "
        "or ask me about labs, scores, or your progress."
    )


def run_test_mode(command: str) -> None:
    """Run the bot in test mode - print response and exit.
    
    Args:
        command: The command to test.
    """
    response = route_command(command)
    print(response)
    sys.exit(0)


async def run_telegram_bot() -> None:
    """Run the Telegram bot."""
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        filters,
    )
    
    config = load_config()
    bot_token = config.get("BOT_TOKEN", "")
    
    if not bot_token:
        print("Error: BOT_TOKEN not found in .env.bot.secret")
        sys.exit(1)
    
    async def telegram_command_handler(update: Update, context) -> None:
        """Handle Telegram commands."""
        # Reconstruct the full command with arguments
        # The command that triggered this handler is in update.message.text
        full_text = update.message.text  # e.g., "/help" or "/scores lab-01"
        print(f"DEBUG: Received command: {full_text}")
        response = route_command(full_text)
        print(f"DEBUG: Response: {response[:50]}...")
        await update.message.reply_text(response)
    
    async def telegram_message_handler(update: Update, context) -> None:
        """Handle regular text messages (for intent routing)."""
        message = update.message.text
        response = route_command(message)
        await update.message.reply_text(response)
    
    # Build application with custom request settings (longer timeouts)
    from telegram.request import HTTPXRequest
    
    request = HTTPXRequest(
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
        pool_timeout=30.0,
    )
    
    app = Application.builder().token(bot_token).request(request).build()
    
    # Add command handlers
    for cmd in COMMAND_HANDLERS.keys():
        cmd_name = cmd.lstrip("/")
        app.add_handler(CommandHandler(cmd_name, telegram_command_handler))
    
    # Add message handler for natural language
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_message_handler))
    
    # Start polling
    print("Starting Telegram bot...")
    await app.initialize()
    await app.start()
    updater = app.updater
    await updater.start_polling()
    
    # Keep running
    while True:
        await asyncio.sleep(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="SE Toolkit Bot")
    parser.add_argument(
        "--test",
        metavar="CMD",
        help="Test mode: run command and print response to stdout",
    )
    
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        asyncio.run(run_telegram_bot())


if __name__ == "__main__":
    main()
