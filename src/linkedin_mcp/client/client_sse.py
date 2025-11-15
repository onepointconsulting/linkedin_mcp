import asyncio
import logging

from mcp.client.sse import sse_client
from linkedin_mcp.config.config import cfg
from linkedin_mcp.client.client_stdio import mcp_profile_search

logger = logging.getLogger(__name__)

"""
Make sure the server is running with the following command:
uv run ./src/linkedin_mcp/server/server.py
"""


async def main(profile: str):

    async with sse_client(f"http://localhost:{cfg.mcp_port}/sse") as (
        read_stream,
        write_stream,
    ):
        await mcp_profile_search(profile, read_stream, write_stream)


if __name__ == "__main__":
    asyncio.run(main("alexander-polev-cto"))
