# Personal Assistant Agent

This project implements a multi-tool personal assistant agent capable of handling various tasks by delegating them to specialized sub-agents.

## Overview

The core of this project is a `MultiToolAgent` that acts as a router, directing user queries to the appropriate sub-agent based on the nature of the request. Currently, the assistant has three main capabilities: handling date and time queries, providing weather information, and managing notes.

## Features

*   **Date & Time Agent (`CurrentDatetimeAgent`):**
    *   Provides the current date and time.
    *   Infers the user's timezone based on their language if not explicitly provided.
    *   Calculates future dates (e.g., "what day will it be in 3 days?").
    *   Determines the day of the week for a given date.

*   **Weather Agent (`WeatherAgent`):**
    *   Provides the current weather for a specified city.
    *   Provides a weather forecast for the next few days (defaults to 3 days).
    *   Understands natural language queries for cities (e.g., "What's the weather in Itajaí?").

*   **Notes Agent (`NotesAgent`):**
    *   Creates, searches, and manages notes on various platforms.
    *   Integrates with MCP (Model Context Protocol) servers to connect to services like Notion.

## Technical Stack

*   **Language:** Python 3.13+
*   **Agent Framework:** `google-adk`
*   **Libraries:**
    *   `pytz`: For robust timezone calculations.
    *   `dateparser`: For parsing human-readable date strings.
*   **APIs:**
    *   `wttr.in`: A console-oriented weather forecast service used by the `WeatherAgent`.
*   **MCP (Model Context Protocol):** For extending the agent's capabilities with external tools.

## Getting Started

To run this project, you will need to have Python 3.13 or higher installed. You will also need to install the dependencies listed in `pyproject.toml`.

```bash
# It is recommended to use a virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv sync
```

### MCP Configuration

This project uses MCP (Model Context Protocol) servers to connect to external services. The configuration for these servers is stored in `mcp.json`. An example configuration for Notion is provided:

```json
// mcp.json
{
  "servers": {
    "mcp-server": {
      "command": "",
      "args": []
    }
  }
}
```

### Environment Variable Configuration

```bash
# .env
GOOGLE_API_KEY=
```

## Usage

You can interact with the personal assistant agent by sending it natural language queries. The agent will automatically route your request to the appropriate sub-agent.

**Examples:**

*   "What time is it in London?"
*   "What day of the week will it be on December 25th, 2025?"
*   "What's the weather like in Tokyo?"
*   "Can I get the weather forecast for New York for the next 5 days?"
*   "Create a new note in Notion with the title 'My Ideas' and the content 'This is a new idea.'"