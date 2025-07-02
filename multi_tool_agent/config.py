from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field


class AgentModel(BaseModel):
    name: str = Field(default="master_assistant_agent")
    model: str = Field(default="gemini-2.5-flash")


class Configs(BaseSettings):
    """Configuration settings for the customer service agent."""

    agent_settings: AgentModel = Field(default=AgentModel())
    app_name: str = "personal_assistant"
