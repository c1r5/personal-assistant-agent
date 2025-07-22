import logging
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseConnectionParams,
    StreamableHTTPConnectionParams,
    StdioConnectionParams,
)
from mcp import StdioServerParameters
from typing import Any, Dict, List, Literal, Tuple, cast


logger = logging.getLogger(__name__)

Transport = Literal["stdio", "sse", "streamable_http", "http"]
MCPServerConfig = Dict[str, Dict[str, str]]
Connection = Dict[str, Any]
DiscoveredServers = Dict[str, Connection]

def _detect_transport(server_config: Dict[str, str]) -> Transport:
    specified_type = server_config.pop("type", None)

    if specified_type is not None:
        return cast(Transport, specified_type)

    if "url" in server_config:
        if "/mcp" in server_config["url"]:
            return "http"
        elif "/sse" in server_config["url"]:
            return "sse"
        else:
            return "streamable_http"

    return "stdio"

def _mcp_config_server_parser(mcp_server_configs: MCPServerConfig) -> DiscoveredServers:
    discovered_servers: DiscoveredServers = {}

    for server_name in mcp_server_configs.keys():
        server_config = mcp_server_configs[server_name]
        discovered_servers[server_name] = {**server_config}
        discovered_servers[server_name]["transport"] = _detect_transport(server_config)

    return discovered_servers


def _load_mcp_toolset(connection: Connection) -> MCPToolset:
    transport_type: Transport = connection["transport"]

    match transport_type:
        case "stdio":
            return MCPToolset(
                connection_params=StdioConnectionParams(
                    timeout=60,
                    server_params=StdioServerParameters(
                        command=connection.get("command", ""),
                        args=connection.get("args", []),
                        env=connection.get("env", {}),
                    ),
                )
            )
        case "sse":
            return MCPToolset(
                connection_params=SseConnectionParams(
                    url=connection.get("url", ""),
                    headers=connection.get("headers", {}),
                    timeout=60,
                )
            )
        case "streamable_http" | "http":
            return MCPToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=connection["url"],
                    headers=connection.get("headers", {}),
                    timeout=60,
                )
            )

def load_mcp_servers(mcp_config: MCPServerConfig) -> Tuple[List[MCPToolset], List[str]]:
    servers = _mcp_config_server_parser(mcp_config)
    tool_names = list(servers.keys())
    toolset = [_load_mcp_toolset(connection) for _, connection in servers.items()]

    logger.info(f"Discovered and Loaded {len(toolset)} tools: {', '.join(tool_names)}")

    return toolset, tool_names
