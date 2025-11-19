from typing import Any
import httpx
from urllib import parse
from mcp.server.fastmcp import FastMCP
import json
import logging
# from dotenv import load_dotenv
import os


# load environment variables
# load_dotenv()

# Initialise FastMCP server
mcp = FastMCP("x")

# Get configuration from environment variables
def get_config():
    return {"bearer_token": os.environ.get("bearer_token", "")}

# constants
API_BASE_URL = 'https://api.x.com'


@mcp.tool(name="get_recent", description="Get recent x posts given a keyword")
async def get_recent(keywords: str) -> str:
    """
    Get recent x posts given a keyword
    :param keywords: query keywords to search for
    :return: JSON
    """
    headers = {
        "Authorization": f"Bearer {get_config()["bearer_token"]}"
    }
    params = {
        "query": keywords
    }
    url = f"{API_BASE_URL}/2/tweets/search/recent"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0, params=params)
            response.raise_for_status()
            logging.debug(response.json())
            # Ensure we return a string (JSON text)
            text = response.text
            logging.info(text)
            return text
        except Exception:
            # Always return a string (error message) so the tool output validates
            return json.dumps({"error": "request_failed"})


def main():
    # Initialise and run the server
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()

