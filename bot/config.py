"""Configuration loading from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict:
    """Load configuration from environment variables.
    
    Looks for .env.bot.secret in the bot directory, falls back to .env.bot.example.
    """
    bot_dir = Path(__file__).parent
    secret_env = bot_dir / ".env.bot.secret"
    example_env = bot_dir / ".env.bot.example"
    
    if secret_env.exists():
        load_dotenv(secret_env)
    elif example_env.exists():
        load_dotenv(example_env)
    
    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_URL": os.getenv("LMS_API_URL", ""),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
    }
