# SE Toolkit Bot Development Plan

## Overview

This document outlines the development plan for the SE Toolkit Telegram Bot, a conversational interface that allows students to check their lab scores, view available labs, and get assistance with their software engineering coursework through Telegram.

## Architecture

The bot follows a **testable handler architecture** where command logic is separated from the Telegram transport layer. Handlers are pure functions that take input (command arguments) and return text responses. They have no dependency on Telegram, enabling offline testing via the `--test` mode.

### Key Components

1. **Entry Point (`bot.py`)**: Handles both Telegram startup and test mode execution
2. **Handlers (`handlers/`)**: Pure functions for each command (`/start`, `/help`, `/health`, `/labs`, `/scores`)
3. **Services (`services/`)**: API clients for LMS integration and LLM-based intent routing
4. **Configuration (`config.py`)**: Environment variable loading from `.env.bot.secret`

## Development Phases

### Phase 1: Scaffold (Task 1)
Create the project structure with `pyproject.toml`, handler stubs, and test mode. This establishes the foundation for all subsequent development.

### Phase 2: Backend Integration (Task 2)
Implement the LMS client to fetch real scores and lab data from the backend API. Replace placeholder responses with actual API calls using `httpx`.

### Phase 3: Intent Routing (Task 3)
Add natural language processing using an LLM to route user queries to appropriate handlers. Users can ask "what labs are available?" instead of typing `/labs`.

### Phase 4: Deployment (Task 4)
Deploy the bot to production, configure environment variables, and ensure reliable operation with proper error handling and logging.

## Testing Strategy

- **Unit Tests**: Test handlers in isolation with various inputs
- **Test Mode**: Use `--test` flag for manual verification without Telegram
- **Integration Tests**: Verify API client behavior with mocked responses
- **End-to-End**: Deploy to staging and test via Telegram

## Dependencies

- `python-telegram-bot`: Telegram Bot API wrapper
- `httpx`: Async HTTP client for API calls
- `python-dotenv`: Environment variable management
