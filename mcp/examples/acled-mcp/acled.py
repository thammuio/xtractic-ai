import os
from typing import Dict
import httpx
from mcp.server.fastmcp import FastMCP
import json
import logging

# Initialise FastMCP server
mcp = FastMCP("acled")

# constants
API_BASE_URL = 'https://acleddata.com'
OAUTH_TOKEN_API = 'https://acleddata.com/oauth/token'


def get_config() -> Dict[str, str]:
    return {
        "username": os.environ.get("username", ""),
        "password": os.environ.get("password", "")
    }


def set_token():
    config = get_config()
    response = httpx.post(OAUTH_TOKEN_API,
                          data={
                              "username": config["username"],
                              "password": config["password"],
                              "grant_type": "password",
                              "client_id": "acled"
                          },
                          headers={"Content-Type": "application/x-www-form-urlencoded"}
                          )
    logging.debug(response.json)
    return response.json()["access_token"]


@mcp.tool(name="acled_read", description="Read acled data for a given country and year of interest")
async def acled_read(country: str, year: str, limit: int = 10) -> str:
    """
    Read acled data for a given country and year of interest
    :param country: the country to search on
    :param year: year of interest
    :param limit: limit the response
    :return: JSON
    """
    # if bearer_token is None:
    bearer_token = set_token()
    logging.info(f"Bearer token: {bearer_token}")

    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "country": country,
        "year": year,
        "limit": limit
    }
    url = f"{API_BASE_URL}/api/acled/read"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0, params=params)
            response.raise_for_status()
            logging.info(response.json())
            # Ensure we return a string (JSON text)
            text = response.text
            logging.debug(text)
            return text
        except Exception:
            # Always return a string (error message) so the tool output validates
            return json.dumps({"error": "request_failed"})


def main():
    # check config from environment variables
    config = get_config()
    req_config = ["username", "password"]
    missing = [k for k in req_config if not config.get(k)]

    if missing:
        logging.error(f"Error: missing config: {', '.join(missing)}")
        exit(1)

    # Initialise and run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()

