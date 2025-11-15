# Use Python 3.13 as base image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Chrome and Chromedriver
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# Install Chromedriver
# Note: webdriver-manager in dependencies can also handle this automatically,
# but we install it explicitly for better performance and reliability
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1) \
    && CHROMEDRIVER_VERSION=$(curl -sS "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_${CHROME_VERSION}" 2>/dev/null || curl -sS "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}" 2>/dev/null || echo "") \
    && if [ -n "$CHROMEDRIVER_VERSION" ] && [ "$CHROMEDRIVER_VERSION" != "" ]; then \
         wget -q -O /tmp/chromedriver.zip "https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip" 2>/dev/null || \
         wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" 2>/dev/null || true; \
         if [ -f /tmp/chromedriver.zip ]; then \
           unzip -q /tmp/chromedriver.zip -d /tmp/; \
           find /tmp -name chromedriver -type f -executable -exec mv {} /usr/local/bin/chromedriver \; 2>/dev/null || true; \
           chmod +x /usr/local/bin/chromedriver 2>/dev/null || true; \
           rm -rf /tmp/chromedriver*; \
         fi; \
       fi

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY README.md ./README.md
COPY pyproject.toml uv.lock* ./
COPY src ./src

# Create virtual environment and sync dependencies
RUN uv venv && \
    uv sync

# Create cookie directory (required by the application)
RUN mkdir -p /var/linkedin/cookies

# Set environment variables
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8050
ENV MCP_TRANSPORT=streamable-http
ENV COOKIE_DIR=/var/linkedin/cookies
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 8050
EXPOSE 8050

# Run the server (equivalent to run_server.sh)
CMD ["uv", "run", "python", "-B", "./src/linkedin_mcp/server/server.py"]

