import json

from google.adk import Agent
from google.genai import types
from google.genai.types import HarmBlockThreshold, HarmCategory

from .mcp_tool import load_tools
from .agents.basic_agents import current_datetime_agent

safety_settings = [
    types.SafetySetting(
        category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,  # Example: adjust as needed
    ),
]

gen_config = types.GenerateContentConfig(
    temperature=0.7, top_p=0.9, safety_settings=safety_settings
)


with open("personal-agent-mcp-servers.json", "r") as f:
    content = json.load(f)

tools = load_tools(content.get("servers", {}))

root_agent = Agent(
    name="MasterPersonalAssistantAgent",
    model="gemini-2.0-flash",
    sub_agents=[current_datetime_agent],
    instruction="""
        You are a helpful assistant thats orchestrates sub assistant. 
        Choose the appropriate assistant based on the user's question. 
        If no assistant call is needed, reply directly.

        Reply requirements:
        1. Reply according to user prompt language

        After receiving a tool's response:
        1. Transform the raw data into a natural, conversational response
        2. Keep responses concise but informative
        3. Focus on the most relevant information
        4. Use appropriate context from the user's question
        5. Avoid simply repeating the raw data
    """,
    generate_content_config=gen_config,
)
