# Apache Knox Gateway Setup

This document provides instructions for setting up and using Apache Knox Gateway with your SSB MCP Server.

## Overview

Apache Knox Gateway has been added to your Docker Compose stack to provide secure access to your SSB services. Knox acts as a reverse proxy and security gateway for your Hadoop ecosystem services.

## Services

The Knox Gateway provides secure access to the following services:

**HTTP Access (port 8082):**
- **SSB SSE**: `http://localhost:8082/gateway/ssb/ssb-sse/`
- **SSB MVE**: `http://localhost:8082/gateway/ssb/ssb-mve/`
- **Kafka**: `http://localhost:8082/gateway/ssb/kafka/`
- **Kafka Connect**: `http://localhost:8082/gateway/ssb/kafka-connect/`
- **Schema Registry**: `http://localhost:8082/gateway/ssb/schema-registry/`
- **Flink**: `http://localhost:8082/gateway/ssb/flink/`
- **NiFi**: `http://localhost:8082/gateway/ssb/nifi/`
- **Qdrant**: `http://localhost:8082/gateway/ssb/qdrant/`

**HTTPS Access (port 8444):**
- **SSB SSE**: `https://localhost:8444/gateway/ssb/ssb-sse/`
- **SSB MVE**: `https://localhost:8444/gateway/ssb/ssb-mve/`
- **Kafka**: `https://localhost:8444/gateway/ssb/kafka/`
- **Kafka Connect**: `https://localhost:8444/gateway/ssb/kafka-connect/`
- **Schema Registry**: `https://localhost:8444/gateway/ssb/schema-registry/`
- **Flink**: `https://localhost:8444/gateway/ssb/flink/`
- **NiFi**: `https://localhost:8444/gateway/ssb/nifi/`
- **Qdrant**: `https://localhost:8444/gateway/ssb/qdrant/`

## Configuration

### Environment Variables for MCP Server

Update your MCP server configuration to use Knox Gateway:

```bash
export KNOX_GATEWAY_URL="http://localhost:8082/gateway/ssb"
export KNOX_TOKEN="your-knox-token"  # Optional: for token-based auth
export KNOX_USER="admin"             # Optional: for basic auth
export KNOX_PASSWORD="admin-password" # Optional: for basic auth
```

### Default Credentials

The Knox Gateway is configured with basic authentication:
- **Username**: `admin`
- **Password**: `admin-password`

### Keystore Configuration

The Knox Gateway uses the following keystore settings:
- **Keystore Password**: `admin\r`
- **Key Password**: `admin\r`
- **Master Secret**: `admin\r`

## Starting the Services

1. Start all services including Knox:
   ```bash
   docker-compose up -d
   ```

2. Wait for Knox to initialize (check logs):
   ```bash
   docker-compose logs knox
   ```

3. Verify Knox is running:
   ```bash
   curl http://localhost:8082/gateway/admin/v1/version
   ```

## Accessing Services Through Knox

### SSB API Access

Instead of accessing SSB directly, use the Knox Gateway:

```bash
# Direct SSB access (bypasses Knox)
curl http://localhost:18121/api/v1/heartbeat

# SSB access through Knox Gateway
curl http://localhost:8082/gateway/ssb/ssb-sse/api/v1/heartbeat
```

### MCP Server Configuration

Update your MCP server to use Knox:

```python
# In your environment or .env file
KNOX_GATEWAY_URL=http://localhost:8082/gateway/ssb
KNOX_USER=admin
KNOX_PASSWORD=admin-password
```

## Security Features

Knox Gateway provides:

1. **Authentication**: Basic auth, LDAP, SAML, OAuth2
2. **Authorization**: Role-based access control
3. **SSL/TLS**: HTTPS termination
4. **Single Sign-On**: Centralized authentication
5. **Audit Logging**: Request/response logging
6. **Rate Limiting**: Protection against abuse

## Customization

### Adding New Services

To add new services to Knox, edit `knox-config/ssb.xml`:

```xml
<service>
  <role>YOUR-SERVICE</role>
  <url>http://your-service:port</url>
</service>
```

### Authentication Methods

The current configuration uses basic authentication. To change this, modify the authentication provider in `knox-config/ssb.xml`.

### SSL Configuration

For production use, update the SSL configuration in `knox-config/gateway-site.xml` with proper certificates.

## Troubleshooting

### Check Knox Status
```bash
docker-compose logs knox
```

### Verify Service Discovery
```bash
curl http://localhost:8082/gateway/ssb/ssb-sse/api/v1/heartbeat
```

### Check Knox Admin API
```bash
curl http://localhost:8082/gateway/admin/v1/version
```

## Port Mapping

- **Knox HTTP**: `8082` (mapped to avoid conflict with Flink on 8081)
- **Knox HTTPS**: `8444` (mapped to avoid conflict with NiFi on 8443)
- **SSB SSE**: `18121` (direct access)
- **SSB MVE**: `18131` (direct access)

## Next Steps

1. Configure your MCP server to use Knox Gateway URLs
2. Set up proper authentication (LDAP, SAML, etc.) for production
3. Configure SSL certificates for HTTPS access
4. Set up monitoring and alerting for Knox Gateway
