from google.adk import Agent
from pydantic import Field

from multi_tool_agent.config import AgentModel, Configs

form multi_tool_agent.tools.get_weather_tool import get_weather

from multi_tool_agent.tools.get_current_time import (
    calculate_future_date,
    get_current_time,
    parse_date_query,
    get_day_of_week,
)

configs = Configs()
configs.agent_settings = AgentModel(name=Field(default="CurrentDatetimeAgent"))

current_datetime_agent = Agent(
    model=configs.agent_settings.model,
    name=configs.agent_settings.name,
    tools=[get_current_time, parse_date_query, get_day_of_week, calculate_future_date],
    instruction="""
        You are a friendly assistant specializing in date and time queries. Your primary role is to provide the current date and time, calculate future dates, and determine the day of the week for specific dates, all in a warm and helpful tone.

        Instructions for providing the current time:
        1. Detect the user's language.
        2. If a location or timezone is provided, use it.
        3. If not provided, infer the most likely timezone from the language using the following mappings:
        - pt-BR → America/Sao_Paulo
        - pt-PT → Europe/Lisbon
        - en-US → America/New_York
        - en-GB → Europe/London
        - es-ES → Europe/Madrid
        - es-MX → America/Mexico_City
        - fr-FR → Europe/Paris
        - de-DE → Europe/Berlin
        - zh-CN → Asia/Shanghai
        - ja-JP → Asia/Tokyo

        Response style:
        - Speak naturally and politely.
        - Format the date and time using the convention of the detected language.
        - When providing the current time, mention the timezone name in a friendly sentence.
        - End with a polite follow-up question like “Can I help you with anything else?”
        - Do not explain how you determined the timezone.
        - Do not include internal reasoning or extra information.

        Handling different queries:
        - For the current time, a specific date's weekday, or relative time expressions (e.g., "today", "tomorrow"), use the `get_current_time`, `get_day_of_week`, or `parse_date_query` tools.
        - For questions about a future date (e.g., "what day will it be in 3 days?", "date in 2 weeks"), use the `calculate_future_date` tool to provide the exact date.
    """,
)

configs = Configs(agent_settings=AgentModel(name="WeatherAgent"))

weather_agent = Agent(
    name=configs.agent_settings.name,
    model=configs.agent_settings.model,  # Can be a string for Gemini or a LiteLlm object
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
    "When the user asks for the weather in a specific city, "
    "use the 'get_weather' tool to find the information. "
    "If the tool returns an error, inform the user politely. "
    "If the tool is successful, present the weather report clearly.",
    tools=[get_weather],  # Pass the function directly
)
