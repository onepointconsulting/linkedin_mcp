source .venv/bin/activate
uv sync
uv run python -B ./src/linkedin_mcp/server/server.py