from google.adk import Agent
from google.genai import types

from config import Configs
from agents import notes_agent, current_datetime_agent

gen_config = types.GenerateContentConfig(temperature=0.7, top_p=0.9)

configs = Configs()

root_agert = Agent(
    name=configs.agent_settings.name,
    model=configs.agent_settings.model,
    sub_agents=[current_datetime_agent, notes_agent],
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
