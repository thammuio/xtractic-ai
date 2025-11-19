from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    # Transport: stdio (default), http, sse
    transport: str = os.getenv("MCP_TRANSPORT", "stdio")
    host: str = os.getenv("MCP_HOST", "127.0.0.1")
    port: int = int(os.getenv("MCP_PORT", "3030"))

    # Knox + SMM
    knox_gateway_url: str = os.getenv("KNOX_GATEWAY_URL", "")
    smm_api_base: Optional[str] = os.getenv("SMM_API_BASE")

    # Auth options
    knox_token: Optional[str] = os.getenv("KNOX_TOKEN") or None
    knox_cookie: Optional[str] = os.getenv("KNOX_COOKIE") or None
    knox_user: Optional[str] = os.getenv("KNOX_USER") or None
    knox_password: Optional[str] = os.getenv("KNOX_PASSWORD") or None
    knox_token_endpoint: Optional[str] = os.getenv("KNOX_TOKEN_ENDPOINT") or None

    # Optional passcode token (e.g., Livy/Knox) for alternate auth patterns
    knox_passcode_token: Optional[str] = os.getenv("KNOX_PASSCODE_TOKEN") or None

    # Direct SMM authentication (when not using Knox)
    smm_user: Optional[str] = os.getenv("SMM_USER") or None
    smm_password: Optional[str] = os.getenv("SMM_PASSWORD") or None

    # TLS/HTTP
    verify_ssl_env: str = os.getenv("KNOX_VERIFY_SSL", "true").lower()
    ca_bundle: Optional[str] = os.getenv("KNOX_CA_BUNDLE")
    timeout_seconds: int = int(os.getenv("HTTP_TIMEOUT_SECONDS", "30"))
    max_retries: int = int(os.getenv("HTTP_MAX_RETRIES", "3"))
    rate_limit_rps: float = float(os.getenv("HTTP_RATE_LIMIT_RPS", "5"))

    # Behavior
    readonly: bool = os.getenv("SMM_READONLY", "true").lower() == "true"
    allowed_actions_csv: str = os.getenv("SMM_ALLOWED_ACTIONS", "")

    # CDP-specific proxy headers
    proxy_context_path: Optional[str] = os.getenv("SMM_PROXY_CONTEXT_PATH")

    def build_verify(self) -> bool | str:
        if self.ca_bundle:
            return self.ca_bundle
        return self.verify_ssl_env not in {"0", "false", "no"}

    def build_smm_base(self) -> str:
        if self.smm_api_base:
            return self.smm_api_base.rstrip("/")
        if not self.knox_gateway_url:
            # Provide more helpful error message
            import os

            env_vars = []
            if os.getenv("SMM_API_BASE"):
                env_vars.append("SMM_API_BASE")
            if os.getenv("KNOX_GATEWAY_URL"):
                env_vars.append("KNOX_GATEWAY_URL")

            if env_vars:
                raise ValueError(
                    f"Environment variables {', '.join(env_vars)} are set but not being read properly. Please check your MCP server configuration."
                )
            else:
                raise ValueError(
                    "KNOX_GATEWAY_URL or SMM_API_BASE must be set. Please configure your MCP server with the appropriate environment variables."
                )
        return f"{self.knox_gateway_url.rstrip('/')}/smm/api/v2"
