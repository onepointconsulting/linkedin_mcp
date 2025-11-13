# LinkedIn MCP

This is a simple implementation of an MCP LinkedIn server using a Selenium Chrome based scraper in the background.

## Pre-requisites

Please install `uv`.

Create a virtual environment and sync the libraries.

```
uv venv
uv sync
```

Then install Chromedriver: https://developer.chrome.com/docs/chromedriver/get-started

## Environment

Make sure you have all of these variables in your .env file:

```
LINKEDIN_USER_1=<user>
LINKEDIN_PASSWORD_1=<pass>

LINKEDIN_USER_2=<user>
LINKEDIN_PASSWORD_2=<pass>

COOKIE_DIR=/var/linkedin/cookies

MCP_HOST=0.0.0.0
MCP_PORT=8050
# Either sse or stdio or streamable-http
MCP_TRANSPORT=streamable-http
MCP_TIMEOUT=150
```

You can use multiple LinkedIn username and password combinations.

### Run in dev mode with MCP Inspector

```
mcp dev ./src/linkedin_mcp/server/server.py
```

### Run with stdio

```
python ./src/linkedin_mcp/client/client_stdio.py
```

### Run the server

```
uv run ./src/linkedin_mcp/server/server.py
```