import json
import logging

from google.adk import Agent
from pydantic import Field
from multi_tool_agent.config import AgentModel, Configs
from multi_tool_agent.tools.mcp_loader import load_mcp_servers

logger = logging.getLogger(__name__ + ".notes-agent")
configs = Configs(agent_settings=AgentModel(name=Field(default="NotesAgent")))

try:
    with open("mcp.json", "r") as f:
        config = json.load(f)

    mcp_tools = load_mcp_servers(config["servers"])
except Exception as e:
    mcp_tools = []
    logger.error("Erro ao obter ferramentas do arquivo: ", exc_info=e)

notes_agent = Agent(
    model=configs.agent_settings.model,
    name=configs.agent_settings.name,
    description="Um agente para criar, buscar e gerenciar anotações em diversas plataformas.",
    instruction="""
      Você é um agente de anotações.
      Sua função é ajudar os usuários a criar, encontrar e gerenciar suas anotações.
      Você tem acesso a ferramentas para interagir com vários serviços de anotações.
      Use essas ferramentas para atender às solicitações do usuário de forma eficiente e precisa.
      Seja proativo e ajude o usuário a organizar suas ideias e informações.

      1. Se não houver ferramentas disponiveis, responda educadamente que você não tem acesso as ferramentas necessárias.
    """,
    tools=[*mcp_tools],
)
