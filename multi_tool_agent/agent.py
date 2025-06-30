from google.adk import Agent
from google.genai.types import HarmCategory, HarmBlockThreshold
from google.genai import types
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from multi_tool_agent.mcp_tool import load_tools

import json


async def create_mcp_agent(
    toolset: list[MCPToolset],
    name: str,
    model: str = "gemini-2.0-flash",
    instruction: str = "",
) -> Agent:
    try:
        safety_settings = [
            types.SafetySetting(
                category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,  # Example: adjust as needed
            ),
        ]

        gen_config = types.GenerateContentConfig(
            temperature=0.7, top_p=0.9, safety_settings=safety_settings
        )

        return Agent(
            model=model,
            name=name,
            tools=[*toolset],
            generate_content_config=gen_config,
            instruction=instruction,
        )
    except Exception as e:
        raise e


with open("personal-agent-mcp-servers.json", "r") as f:
    content = json.load(f)

tools = load_tools(content.get("servers", {}))

root_agent = Agent(
    name="personal_assistant_agent", model="gemini-1.5-pro-002", tools=[*tools]
)
