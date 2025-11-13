import asyncio
import logging
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.session import MemoryObjectReceiveStream, MemoryObjectSendStream, SessionMessage
from mcp.client.stdio import stdio_client
from mcp.types import ListToolsResult, CallToolResult


logger = logging.getLogger(__name__)


async def main(profile: str):
    # Load environment variables from .env file
    # This ensures variables like COOKIE_DIR, LINKEDIN_USER_*, etc. are available
    # Try to find .env file in project root (4 levels up from this file)
    project_root = Path(__file__).parent.parent.parent.parent
    env_file = project_root / ".env"

    # Load .env file if it exists, otherwise load_dotenv() will try current directory
    if env_file.exists():
        load_dotenv(env_file, override=False)  # Don't override existing env vars
        logger.info(f"Loaded environment variables from {env_file}")
    else:
        # Fallback: try loading from current directory
        load_dotenv(override=False)
        logger.info("Attempted to load environment variables from .env file")

    # Log which environment variables are loaded (without sensitive values)
    env_vars_loaded = [
        key
        for key in os.environ.keys()
        if key.startswith(("LINKEDIN_", "COOKIE_", "MCP_", "CHROME"))
    ]
    if env_vars_loaded:
        logger.info(
            f"Environment variables available: {', '.join(sorted(env_vars_loaded))}"
        )

    # Create server parameters with environment variables
    # os.environ.copy() includes all environment variables including those from .env
    server_params = StdioServerParameters(
        command="python",
        args=["src/linkedin_mcp/server/server.py", "stdio"],
        env=os.environ.copy(),  # Pass all environment variables to the server subprocess
        cwd=project_root,  # Set working directory to project root
    )
    async with stdio_client(server_params) as (read_stream, write_stream):
        await mcp_profile_search(read_stream, write_stream, profile)


async def mcp_profile_search(
    profile: str,
    read_stream: MemoryObjectReceiveStream[SessionMessage | Exception],
    write_stream: MemoryObjectSendStream[SessionMessage],
):
    async with ClientSession(read_stream, write_stream) as session:
        await session.initialize()

        tools: ListToolsResult = await session.list_tools()
        logger.info(f"{len(tools.tools)} tools found")

        tool_result: CallToolResult = await session.call_tool(
            name="linkedin_profile",
            arguments={
                "profile": profile,
            },
        )
        if len(tool_result.content) > 0:
            structured_data = json.loads(tool_result.content[0].text)
            print(json.dumps(structured_data, indent=2))
        else:
            print("error calling tool")


if __name__ == "__main__":
    asyncio.run(main("alexander-polev-cto"))
