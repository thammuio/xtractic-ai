# Register MCP Server
For security reasons, Cloudera Agent Studio does not save environment variable values. The values would need to be entered again while configuring a workflow. It is recommended to use dummy values here for the environment variables.

MCP Server Configuration Examples:
```installation
{
  "mcpServers": {
    "iceberg-mcp-server": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/cloudera/iceberg-mcp-server@main",
        "run-server"
      ],
      "env": {
        "IMPALA_HOST": "coordinator-default-impala.example.com",
        "IMPALA_PORT": "443",
        "IMPALA_USER": "username",
        "IMPALA_PASSWORD": "password",
        "IMPALA_DATABASE": "default"
      }
    }
  }
}
```

```example
{
  "mcpServers": {
    "Example MCP Server": {
      "command": "uvx",
      "args": ["mcp-server-time", "--local-timezone=America/New_York"],
      "env": {}
    }
  }
}
```

```x-social-mcp-server
{
  "properties": {
    "keywords": {
      "title": "Keywords",
      "type": "string"
    }
  },
  "required": [
    "keywords"
  ],
  "title": "get_recentArguments",
  "type": "object"
}
```

```get_current_time
{
  "type": "object",
  "properties": {
    "timezone": {
      "type": "string",
      "description": "IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'America/New_York' as local timezone if no timezone provided by the user."
    }
  },
  "required": [
    "timezone"
  ]
}
```

```convert_time
{
  "type": "object",
  "properties": {
    "source_timezone": {
      "type": "string",
      "description": "Source IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'America/New_York' as local timezone if no source timezone provided by the user."
    },
    "time": {
      "type": "string",
      "description": "Time to convert in 24-hour format (HH:MM)"
    },
    "target_timezone": {
      "type": "string",
      "description": "Target IANA timezone name (e.g., 'Asia/Tokyo', 'America/San_Francisco'). Use 'America/New_York' as local timezone if no target timezone provided by the user."
    }
  },
  "required": [
    "source_timezone",
    "time",
    "target_timezone"
  ]
}
```




The MCP Server name would be Example MCP Server. The sub-key under "mcpServers" can be used to change the name.
Only uvx (for Python-based) and npx (for Node.js-based) are supported as runtimes for MCP servers currently.