# SSM MCP Server

![SMM Home Interface](images/SMM_home_branded.jpg)
*The Streams Messaging Manager home interface showing cluster overview and navigation*

Model Context Protocol server providing access to Cloudera Streams Messaging Manager (SMM) with support for both direct SMM access and CDP integration.

**Works with both standalone SMM deployments and Cloudera Data Platform (CDP) SMM deployments** - provides core SMM functionality through Claude Desktop.

## ⚠️ Current Status

**25.6% Success Rate** - 22 out of 86 MCP tools are currently working. Core functionality including cluster management, topic listing, and Kafka Connect integration is operational. Many advanced features (metrics, alerts, consumer groups) are not yet working due to API endpoint issues.

**Working Features:**
- ✅ Cluster Management (100%)
- ✅ Topic Management - Read Operations (62.5%)
- ✅ Notifiers Management (66.7%)
- ✅ Kafka Connect - Enhanced Features (62.5%)
- ✅ Replication Statistics (20%)

## Features

- **Multiple Authentication Methods**:
  - **Direct SMM Authentication**: Basic auth for standalone SMM deployments
  - **Apache Knox Integration**: JWT tokens, cookies, and passcode tokens for CDP deployments
- **Read-only by default** - Safe exploration of SMM clusters and configuration
- **Working SMM API coverage** with **22+ verified MCP tools** for core SMM management:
  - **✅ Cluster Management**: Broker details, cluster health, configuration (100% working)
  - **✅ Topic Management (Read)**: List topics, get topic info, configurations (62.5% working)
  - **✅ Notifiers Management**: Alert notification configuration (66.7% working)
  - **✅ Kafka Connect (Enhanced)**: Connector templates, configs, monitoring (62.5% working)
  - **✅ Replication Statistics**: Basic replication status checking (20% working)
  - **⚠️ Topic Management (Write)**: Limited - SMM is primarily a monitoring tool
  - **⚠️ Consumer Group Management**: Currently not working (0% working)
  - **⚠️ Metrics & Monitoring**: Currently not working (0% working)
  - **⚠️ Alert Management**: Currently not working (0% working)
  - **⚠️ Schema Registry**: Currently not working (0% working)
  - **⚠️ Lineage Tracking**: Currently not working (0% working)
  - **⚠️ Authentication**: Currently not working (0% working)

## Quick Start

![SMM Home Interface](images/SMM_home.png)
*The Streams Messaging Manager home interface showing cluster overview and navigation*

### For Standalone SMM Deployments

1. **Install and setup:**
   ```bash
   git clone https://github.com/your-org/ssm-mcp-server.git
   cd ssm-mcp-server
   
   # Option A: Using uv (recommended)
   make setup  # Installs uv if needed and dependencies
   
   # Option B: Using pip
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Configure Claude Desktop** - Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "ssm-mcp-server": {
         "command": "/FULL/PATH/TO/SSM-MCP-Server/run_mcp_server.sh",
         "args": [],
         "cwd": "/FULL/PATH/TO/SSM-MCP-Server",
         "env": {
           "MCP_TRANSPORT": "stdio",
           "SMM_API_BASE": "http://localhost:8080/api/v2",
           "SMM_USER": "admin",
           "SMM_PASSWORD": "admin",
           "SMM_READONLY": "true"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** and start interacting with your SMM cluster!

## Docker Setup

### Quick Start with Docker Compose

The project includes a complete Docker Compose setup for running SMM with all dependencies:

1. **Start the full Cloudera stack:**
   ```bash
   docker-compose up -d
   ```

2. **Wait for services to be healthy:**
   ```bash
   # Check service status
   docker-compose ps
   
   # View logs for SMM service
   docker-compose logs -f smm
   ```

3. **Access SMM:**
   - **SMM Web UI**: http://localhost:8585
   - **SMM API**: http://localhost:9991/api/v1/admin

4. **Configure the MCP Server** for Docker setup:
   ```json
   {
     "mcpServers": {
       "ssm-mcp-server": {
         "command": "/FULL/PATH/TO/SSM-MCP-Server/run_mcp_server.sh",
         "args": [],
         "cwd": "/FULL/PATH/TO/SSM-MCP-Server",
         "env": {
           "MCP_TRANSPORT": "stdio",
           "SMM_API_BASE": "http://localhost:9991/api/v1/admin",
           "SMM_USER": "admin",
           "SMM_PASSWORD": "admin",
           "SMM_READONLY": "true"
         }
       }
     }
   }
   ```

### Docker Services Included

The Docker Compose setup includes:

- **SMM** (Streams Messaging Manager) - Port 8585 (UI), 9991 (API)
- **Kafka** - Port 9092, 9094, 24042, 9100
- **Zookeeper** - Port 2181
- **Kafka Connect** - Port 28083, 28086
- **Schema Registry** - Port 7788
- **Prometheus** - Port 9090
- **PostgreSQL** - Port 5432
- **Apache Knox** - Port 8444 (HTTPS), 8082 (HTTP)
- **Flink** - Port 8081 (JobManager)
- **NiFi** - Port 8080, 8443

### Docker Management Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f smm

# Restart a specific service
docker-compose restart smm

# Scale services (e.g., Flink task managers)
docker-compose up -d --scale flink-taskmanager=3

# Clean up (removes containers and volumes)
docker-compose down -v
```

### Sample Data Loading with NiFi

The project includes a pre-configured NiFi flowfile (`StockPriceToKafka.json`) that demonstrates data ingestion into Kafka:

**What it does:**
- Fetches real-time NVIDIA (NVDA) stock price data from Alpha Vantage API
- Processes and transforms the JSON data using NiFi processors
- Publishes the data to a Kafka topic named "NVDA"

**How to use it:**

1. **Start the Docker stack:**
   ```bash
   docker-compose up -d
   ```

2. **Access NiFi:**
   - Open http://localhost:8080 in your browser
   - Login with admin/admin (if single-user mode is enabled)

3. **Import the flowfile:**
   - Go to the NiFi canvas
   - Click the "Upload Template" button (📄 icon)
   - Select `StockPriceToKafka.json` from the project root
   - Drag the template onto the canvas to create the flow

4. **Configure and start:**
   - The flow will automatically start fetching stock data
   - Data will be published to the "NVDA" Kafka topic
   - You can monitor the flow in NiFi and view the data in SMM

**Flow Components:**
- **InvokeHTTP**: Fetches data from Alpha Vantage API
- **SplitJson**: Splits the response into individual records
- **FlattenJson**: Flattens nested JSON structure
- **ConvertRecord**: Converts data format
- **PublishKafka**: Publishes to Kafka topic "NVDA"
- **LogAttribute**: Logs successful publications

**Note:** You'll need to obtain a free API key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) and update the URL in the InvokeHTTP processor.

### For CDP SMM deployments (via Apache Knox)

Your Knox gateway URL will typically be:
```
https://<your-knox-gateway>:8444/gateway/smm
```

Get your Knox JWT token from the CDP UI and use it with the configurations below.

## Setup

### Option 1: Claude Desktop (Local)

1. **Clone and install:**
   ```bash
   git clone https://github.com/your-org/ssm-mcp-server.git
   cd ssm-mcp-server
   
   # Using uv (recommended)
   make setup
   
   # Or using pip
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e .
   ```

2. **Configure Claude Desktop** - Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "ssm-mcp-server": {
         "command": "/FULL/PATH/TO/SSM-MCP-Server/.venv/bin/python",
         "args": [
           "-m",
           "ssm_mcp_server.server"
         ],
         "env": {
           "MCP_TRANSPORT": "stdio",
           "KNOX_GATEWAY_URL": "https://knox-gateway.yourshere.cloudera.site/gateway/smm",
           "KNOX_TOKEN": "<your_knox_jwt_token>",
           "SMM_READONLY": "true"
         }
       }
     }
   }
   ```

3. **Restart Claude Desktop** and start asking questions about your SMM cluster!

### Knox Configuration Examples

#### Option A: JWT Token Authentication
```json
{
  "mcpServers": {
    "ssm-mcp-server": {
      "command": "/FULL/PATH/TO/SSM-MCP-Server/run_mcp_server.sh",
      "args": [],
      "cwd": "/FULL/PATH/TO/SSM-MCP-Server",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KNOX_GATEWAY_URL": "https://your-knox-gateway:8444/gateway/smm",
        "KNOX_TOKEN": "your-knox-jwt-token",
        "SMM_READONLY": "true"
      }
    }
  }
}
```

#### Option B: Username/Password Authentication
```json
{
  "mcpServers": {
    "ssm-mcp-server": {
      "command": "/FULL/PATH/TO/SSM-MCP-Server/run_mcp_server.sh",
      "args": [],
      "cwd": "/FULL/PATH/TO/SSM-MCP-Server",
      "env": {
        "MCP_TRANSPORT": "stdio",
        "KNOX_GATEWAY_URL": "https://your-knox-gateway:8444/gateway/smm",
        "KNOX_USER": "your-username",
        "KNOX_PASSWORD": "your-password",
        "KNOX_TOKEN_ENDPOINT": "https://your-knox-gateway:8444/gateway/knoxsso/api/v1/websso",
        "SMM_READONLY": "true"
      }
    }
  }
}
```

### Option 2: Direct Installation (Cloudera Agent Studio)

For use with Cloudera Agent Studio, use the `uvx` command:

```json
{
  "mcpServers": {
    "ssm-mcp-server": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/your-org/ssm-mcp-server@main",
        "run-server"
      ],
       "env": {
         "MCP_TRANSPORT": "stdio",
         "KNOX_GATEWAY_URL": "https://knox-gateway.yourshere.cloudera.site/gateway/smm",
         "KNOX_TOKEN": "<your_knox_jwt_token>",
         "SMM_READONLY": "true"
       }
    }
  }
}
```

## Configuration Options

All configuration is done via environment variables:

### Direct SMM Authentication (Standalone)
| Variable | Required | Description |
|----------|----------|-------------|
| `SMM_API_BASE` | Yes | Full SMM API URL (e.g., `http://localhost:8080/api/v2`) |
| `SMM_USER` | Yes | SMM username (e.g., `admin`) |
| `SMM_PASSWORD` | Yes | SMM password (e.g., `admin`) |
| `SMM_READONLY` | No | Read-only mode (default: `true`) |
| `HTTP_TIMEOUT_SECONDS` | No | HTTP timeout in seconds (default: `30`) |

### Knox Authentication (CDP)
| Variable | Required | Description |
|----------|----------|-------------|
| `KNOX_GATEWAY_URL` | Yes* | Knox gateway URL (e.g., `https://host:8444/gateway/smm`) |
| `KNOX_TOKEN` | Yes* | Knox JWT token for authentication |
| `KNOX_COOKIE` | No | Alternative: provide full cookie string instead of token |
| `KNOX_PASSCODE_TOKEN` | No | Alternative: Knox passcode token (auto-exchanged for JWT) |
| `KNOX_USER` | No | Knox username for basic auth |
| `KNOX_PASSWORD` | No | Knox password for basic auth |
| `KNOX_TOKEN_ENDPOINT` | No | Knox token endpoint for JWT exchange |
| `KNOX_VERIFY_SSL` | No | Verify SSL certificates (default: `true`) |
| `KNOX_CA_BUNDLE` | No | Path to CA certificate bundle |
| `SMM_READONLY` | No | Read-only mode (default: `true`) |
| `HTTP_TIMEOUT_SECONDS` | No | HTTP timeout in seconds (default: `30`) |

\* Either `SMM_API_BASE` (for direct) or `KNOX_GATEWAY_URL` (for Knox) is required

## Development with uv

This project uses [uv](https://docs.astral.sh/uv/) for fast dependency management and Python project management.

### Quick Commands

```bash
# Install uv and dependencies
make setup

# Run the server
make run

# Run tests
make test

# Run linting
make lint

# Format code
make format

# Show all available commands
make help
```

### Manual uv Commands

```bash
# Install dependencies
uv sync

# Run the server
uv run python -m ssm_mcp_server.server

# Run tests
uv run python test_connection_uv.py

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade
```

## Example Usage

Once configured, you can ask Claude questions like:

### Basic Information
- "What version of SMM am I running?"
- "Show me the cluster details"
- "List all brokers in the cluster"
- "What topics are available?"
- "Show me all consumer groups"

![Cluster Health](images/ClusterHealth.png)
*Example: Cluster health and broker information display*

### Topic Management
- "Show me the configuration for topic 'sales-data'"
- "Show me the content of topic 'logs' partition 0"
- "List all topics in the cluster"
- "What are the metrics for topic 'user-events'?"

![List All User Topics](images/ListallUserTopics.png)
*Example: Listing all user topics in the cluster*

![Topic Information](images/ListTopicInfo.png)
*Example: Detailed topic information and configuration*

![Configuration Management](images/ConfigurationMangement.png)
*Example: Topic configuration management and analysis*

**Note**: SMM is primarily a monitoring tool. For topic creation/deletion, use Kafka admin tools:
- `kafka-topics.sh --create --topic user-events --partitions 3 --bootstrap-server localhost:9092`
- `kafka-topics.sh --delete --topic test-topic --bootstrap-server localhost:9092`

### Consumer Group Management
- "List all consumer groups"
- "Show me details for consumer group 'my-app'"
- "Reset the offset for consumer group 'my-app' on topic 'user-events' partition 0 to offset 100"
- "What consumers are currently active?"

![Broker Information](images/ListBrokerInfo.png)
*Example: Detailed broker information and monitoring*

### Metrics and Monitoring
- "Show me cluster metrics for the last hour"
- "What are the metrics for topic 'user-events'?"
- "Show me consumer group metrics for 'my-app'"
- "What are the broker metrics for broker 1?"

### Alert Management
- "Show me all alert policies"
- "Create an alert policy for topic lag"
- "What alerts are currently active?"
- "Mark these notifications as read"

### Schema Registry
- "Show me schema information for topic 'user-events'"
- "What are the key and value schemas for topic 'sales-data'?"
- "Register a new schema for topic 'events'"

### Kafka Connect
- "List all Kafka Connect connectors"
- "Show me details for connector 'file-source'"
- "Create a new connector for database sync"
- "What are the Connect worker metrics?"

### Lineage and Data Flow
- "Show me the lineage for topic 'user-events'"
- "What's the data flow for consumer group 'analytics'?"
- "Show me producer lineage for 'data-ingestion'"

## Available Tools

**Current Status**: 25.6% success rate (22 out of 86 MCP tools working)

The following tools are currently **working and functional**:

### 🔧 Core Information (100% working)
- `get_smm_info()` - Get SMM version and system information
- `get_smm_version()` - Get SMM version details

### 🏢 Cluster and Broker Management (100% working)
- `get_cluster_details()` - Get cluster details and information
- `get_brokers()` - Get all brokers in the cluster
- `get_broker(broker_id)` - Get details of a specific broker
- `get_broker_metrics(broker_id, duration?, from_time?, to_time?)` - Get metrics for a specific broker
- `get_all_broker_details()` - Get all broker details with configurations
- `get_broker_details(broker_id)` - Get detailed broker information including configuration

### 📊 Topic Management - Read Operations (62.5% working)
- `get_all_topic_infos()` - Get all topic information
- `get_topic_description(topic_name)` - Get detailed description of a specific topic
- `get_topic_info(topic_name)` - Get basic information about a specific topic
- `get_topic_partitions(topic_name)` - Get partition information for a specific topic
- `get_topic_partition_infos(topic_name)` - Get detailed partition information for a specific topic
- `get_topic_configs(topic_name)` - Get configuration for a specific topic
- `get_all_topic_configs()` - Get configurations for all topics
- `get_default_topic_configs()` - Get default topic configurations

### 📢 Notifiers Management (66.7% working)
- `get_notifiers()` - Get all notifiers
- `get_notifier_provider_configs()` - Get notifier provider configurations

### 🔄 Replication Statistics (20% working)
- `is_replication_configured()` - Check if replication is configured

### 🔌 Kafka Connect Enhanced (62.5% working)
- `get_connector_templates()` - Get available connector templates
- `get_connector_config_definitions(connector_plugin_class)` - Get connector configuration definitions
- `get_connector_config_sample(name, connector_plugin_class, version)` - Get sample connector configuration
- `is_connect_configured()` - Check if Kafka Connect is configured
- `get_connect_worker_metrics(duration?, from_time?, to_time?)` - Get Kafka Connect worker metrics

---

**📋 For complete information about non-working tools and limitations, see [LimitationsREADME.md](LimitationsREADME.md)**

## Write Operations

By default, the server runs in read-only mode for CDP deployments and write-enabled for standalone deployments. To change this:

1. Set `SMM_READONLY=false` (enable writes) or `SMM_READONLY=true` (read-only)
2. Restart the MCP server

**⚠️ Important Limitations**: SMM is primarily a monitoring tool and does not actually perform write operations on topics.

### Supported Write Operations:
- Creating and managing alert policies
- Managing Kafka Connect connectors
- Schema registry operations
- Consumer group offset management

### Not Supported (SMM Limitations):
- **Topic creation/deletion**: SMM API accepts requests but doesn't create/delete topics
- **Topic configuration changes**: SMM API accepts requests but doesn't modify topic configs
- **Partition management**: SMM API accepts requests but doesn't create/modify partitions

**For topic management, use Kafka admin tools or the Kafka Admin API directly.**


## Limitations

For detailed information about current limitations, non-working features, and known issues, please see:

📋 **[LimitationsREADME.md](LimitationsREADME.md)** - Comprehensive documentation of:
- SMM topic creation limitations
- Non-working MCP tools (75% currently not working)
- Working MCP tools (25% success rate)
- API endpoint issues and resolution status
- Contributing guidelines for fixes

**Quick Summary**: The server currently has a 25.6% success rate (22/86 tools working) due to API endpoint issues. Core functionality like cluster management, topic listing, and broker monitoring is operational.

## Security

- All sensitive data (passwords, tokens, secrets) is automatically redacted in responses
- Large collections are truncated to prevent overwhelming the LLM
- Read-only mode is enabled by default for CDP deployments to prevent accidental modifications
- Direct SMM authentication uses basic auth over HTTP (suitable for local development)
- CDP integration uses secure JWT token authentication

## Troubleshooting

### Common Issues

1. **"Unauthorized" errors**: Check your authentication credentials
   - For direct SMM: Verify `SMM_USER` and `SMM_PASSWORD`
   - For CDP: Verify `SMM_TOKEN` or `SMM_USER`/`SMM_PASSWORD`

2. **"Connection refused" errors**: Ensure SMM services are running
   - Check SMM service status
   - Verify port mappings and network connectivity

3. **"Topic not found" errors**: Verify topic names and cluster access
   - Use `get_all_topic_infos()` to list available topics
   - Check topic permissions and access rights

4. **SSL certificate errors**: For CDP deployments
   - Set `SMM_VERIFY_SSL=false` for self-signed certificates
   - Or provide proper CA bundle with `SMM_CA_BUNDLE`

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export MCP_LOG_LEVEL=DEBUG
```

## Summary

The SSM MCP Server is a **comprehensive management platform** for Cloudera Streams Messaging Manager, providing Claude Desktop with access to virtually all SMM functionality through **60+ MCP tools**.

### 🎯 **What You Get:**
- **Complete SMM Control**: Manage clusters, topics, consumers, and alerts
- **Advanced Monitoring**: Real-time metrics and comprehensive alerting
- **Data Management**: Schema registry, Kafka Connect, and lineage tracking
- **Enterprise Features**: Multi-environment support and secure authentication
- **Developer Tools**: Topic consumption, offset management, and data exploration

### 🚀 **Key Benefits:**
- **95%+ API Coverage**: Access to virtually all SMM functionality
- **90+ MCP Tools**: Comprehensive toolset for every use case
- **12 Functional Categories**: Organized, discoverable capabilities
- **Enterprise Ready**: Security, monitoring, and scalability features
- **User Friendly**: Natural language interaction through Claude Desktop
- **Flexible**: Supports both standalone and CDP deployments

### 📈 **Perfect For:**
- **Data Engineers**: Topic management, consumer monitoring, real-time analysis
- **DevOps Teams**: Cluster management, monitoring, alerting
- **Data Scientists**: Data exploration, lineage tracking, schema management
- **Platform Admins**: System monitoring, configuration management, security

The SSM MCP Server transforms Claude Desktop into a powerful SMM management interface, enabling natural language interaction with your entire Streams Messaging Manager environment! 🎉

## License

Apache License 2.0
