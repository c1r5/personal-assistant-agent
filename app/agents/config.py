from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field


class AgentModel(BaseModel):
    name: str = Field(default="MasterAssistantAgent")
    model: str = Field(default="gemini-1.5-pro-002")


class Configs(BaseSettings):
    """Configuration settings for the customer service agent."""

    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "personal_assistant"
