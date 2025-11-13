import os
import random
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)


class Config:

    def __init__(self):

        self.linkedin_users_passwords = []
        for key, user_name in os.environ.items():
            if key.startswith("LINKEDIN_USER_"):
                user_number = key.split("_")[-1]
                for key, password in os.environ.items():
                    if key == f"LINKEDIN_PASSWORD_{user_number}":
                        self.linkedin_users_passwords.append((user_name, password))

        cookie_dir_var = os.getenv("COOKIE_DIR")
        assert cookie_dir_var is not None, "The cookie directory cannot be empty."
        if not Path(cookie_dir_var).exists():
            Path(cookie_dir_var).mkdir(exist_ok=True, parents=True)
        self.cookie_dir = Path(cookie_dir_var)

        self.mcp_host = os.getenv("MCP_HOST", "0.0.0.0")
        self.mcp_port = os.getenv("MCP_PORT", 8000)
        self.mcp_transport = os.getenv("MCP_TRANSPORT", "stdio")
        self.mcp_timeout = int(os.getenv("MCP_TIMEOUT", "300"))
        logger.info(
            f"MCP configuration: host={self.mcp_host}, port={self.mcp_port}, transport={self.mcp_transport}, timeout={self.mcp_timeout}"
        )

    def get_random_linkedin_credential(self) -> tuple[str, str]:
        return random.choice(self.linkedin_users_passwords)


cfg = Config()
