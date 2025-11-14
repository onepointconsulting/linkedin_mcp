# Run the MCP server without bytecode caching
# This ensures code changes are always picked up

Write-Host "Starting LinkedIn MCP server (no bytecode cache)..." -ForegroundColor Green
uv run python -B ./src/linkedin_mcp/server/server.py

