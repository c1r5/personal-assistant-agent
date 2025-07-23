from google.adk import Agent
from google.adk.tools.mcp_tool import (
    MCPToolset,
    StdioConnectionParams,
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters
from google.genai import types

import logging

from agents.config import Configs
from agents.sub_agents.basic_agents import current_datetime_agent
from helpers import getenv_or_raise
import json

logger = logging.getLogger(__name__)

gen_config = types.GenerateContentConfig(temperature=0.7, top_p=0.9)

configs = Configs()

# try:
#     root_path = find_project_root(__file__)

#     if not root_path:
#         raise ValueError("Project root not found")

#     mcp_file = list(Path(root_path).rglob("mcp.json"))[0]

#     with open(mcp_file, "r") as f:
#         config = json.load(f)

#     mcp_tools, mcp_tool_names = load_mcp_servers(config["servers"])
#     MCP_INSTRUCTION = f"""Your goal is to answer the user's request using the available tools.
# The following MCP tools are at your disposal: {', '.join(mcp_tool_names)}
# """
#     logger.info(f"Loaded MCP tools: {', '.join(mcp_tool_names)}")
# except Exception as e:
#     mcp_tools = []
#     MCP_INSTRUCTION = "No MCP tools were loaded."
#     logger.error("Error getting tools from file: ", exc_info=e)

notion_agent = Agent(
    name="NotionAgent",
    description="A specialized agent that can interact with Notion tools.",
    model=configs.agent_settings.model,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                timeout=60,
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "@notionhq/notion-mcp-server"],
                    env={
                        "OPENAPI_MCP_HEADERS": json.dumps(
                            {
                                "Authorization": "Bearer "
                                + getenv_or_raise("NOTION_API_KEY"),
                                "Notion-Version": "2022-06-28",
                            }
                        )
                    },
                ),
            )
        )
    ],
    generate_content_config=gen_config,
    instruction="""
    You are a specialized Notion agent integrated into an MCP (Model Context Protocol) environment. Your primary function is to interact with Notion through the available MCP tools, acting as an intelligent interface between the user and Notion's API.

    You must strictly rely on the provided tools for any operation involving Notion (e.g., 'list pages in a database', 'fetch a block’s content', 'update a page property', 'append a new block').

    1. **Understand the user intent:** Interpret the user's request precisely and determine what kind of interaction with Notion is required.
    2. **Use only available tools:** Do not fabricate answers or hallucinate content. Select and call the appropriate tool for the request.
    3. **Call tools with precision:** Provide complete and accurate parameters when invoking a tool (e.g., database_id, page_id, block_id, filters).
    4. **Structure the result:** Return the results in a clean, structured, and easy-to-understand format. Avoid dumping raw JSON unless explicitly requested.
    5. **Maintain context awareness:** Reuse relevant context like previously selected databases, pages, or filters to provide a smoother and more helpful user experience.

    You operate in a stateless environment unless the system provides memory. Always assume your current knowledge comes from the last interaction and tool result. Be concise, accurate, and aligned with the actual state of the Notion workspace.

    Your goal is to be a reliable and intelligent interface to Notion, capable of streamlining workflows, surfacing insights, and reducing the friction of using Notion through MCP.
""",
)

github_agent = Agent(
    name="GithubAgent",
    description="A specialized agent that can interact with GitHub tools.",
    model=configs.agent_settings.model,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://api.githubcopilot.com/mcp/",
                headers={
                    "Authorization": "Bearer "
                    + getenv_or_raise("GITHUB_PERSONAL_ACCESS_TOKEN"),
                },
            )
        )
    ],
    generate_content_config=gen_config,
    instruction="""
    You are a specialized GitHub agent. Your primary function is to interact with the GitHub API using the available tools to perform tasks as requested by the user.

    When a user asks for something related to GitHub (e.g., 'list repository issues', 'get pull request details', 'create a new branch'), you must use the provided tools.

    1.  **Analyze the request:** Carefully understand what the user wants to achieve on GitHub.
    2.  **Select the right tool:** Choose the most appropriate tool from your toolset to fulfill the request.
    3.  **Execute the tool:** Call the tool with the correct parameters based on the user's input.
    4.  **Format the output:** Present the result from the tool in a clear and user-friendly way. Do not just dump the raw output.

    Your goal is to be an efficient and accurate interface to GitHub.""",
)

root_agent = Agent(
    name=configs.agent_settings.name,
    model=configs.agent_settings.model,
    sub_agents=[current_datetime_agent, github_agent, notion_agent],
    generate_content_config=gen_config,
    instruction="""
        You are a helpful assistant thats orchestrates sub assistant.
        Choose the appropriate assistant based on the user's question.
        If no assistant call is needed, reply directly.

        Reply requirements:
        1. IMPORTANT: ALWAYS Reply according to user language

        After receiving a tool's response:
        1. Transform the raw data into a natural, conversational response
        2. Keep responses concise but informative
        3. Focus on the most relevant information
        4. Use appropriate context from the user's question
        5. Avoid simply repeating the raw data
    """,
)
