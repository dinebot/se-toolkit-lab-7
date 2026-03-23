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
from handlers.intent_router import IntentRouter
from services.lms_client import LMSClient
from services.llm_client import LLMClient


# Command routing map
COMMAND_HANDLERS = {
    "/start": handle_start,
    "/help": handle_help,
    "/health": handle_health,
    "/labs": handle_labs,
    "/scores": handle_scores,
}


def get_intent_router() -> IntentRouter:
    """Create an intent router instance."""
    config = load_config()
    lms_client = LMSClient(
        base_url=config["LMS_API_URL"],
        api_key=config["LMS_API_KEY"],
    )
    llm_client = LLMClient(
        api_key=config["LLM_API_KEY"],
        base_url=config.get("LLM_API_BASE_URL", "http://localhost:42005/v1"),
        model=config.get("LLM_API_MODEL", "qwen3-coder-flash"),
    )
    return IntentRouter(lms_client, llm_client)


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
    # Use LLM to understand the query and call appropriate tools
    router = get_intent_router()
    return asyncio.run(router.route(command))


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
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

    # Inline keyboard for common actions
    main_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🏥 Health", callback_data="/health"),
            InlineKeyboardButton("📋 Labs", callback_data="/labs"),
        ],
        [
            InlineKeyboardButton("📊 Scores", callback_data="/scores lab-04"),
            InlineKeyboardButton("❓ Help", callback_data="/help"),
        ],
    ])

    async def telegram_command_handler(update: Update, context) -> None:
        """Handle Telegram commands."""
        full_text = update.message.text
        print(f"DEBUG: Received command: {full_text}")
        response = route_command(full_text)
        print(f"DEBUG: Response: {response[:50]}...")
        await update.message.reply_text(response, reply_markup=main_keyboard)

    async def telegram_message_handler(update: Update, context) -> None:
        """Handle regular text messages (for intent routing)."""
        message = update.message.text
        response = route_command(message)
        await update.message.reply_text(response, reply_markup=main_keyboard)

    async def telegram_callback_handler(update: Update, context) -> None:
        """Handle inline keyboard button clicks."""
        query = update.callback_query
        await query.answer()
        callback_data = query.data
        print(f"DEBUG: Callback: {callback_data}")
        response = route_command(callback_data)
        await query.edit_message_text(response, reply_markup=main_keyboard)
    
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

    # Add callback handler for inline keyboard
    from telegram.ext import CallbackQueryHandler
    app.add_handler(CallbackQueryHandler(telegram_callback_handler))
    
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
