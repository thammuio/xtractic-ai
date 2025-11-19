#!/bin/bash

# Knox Gateway initialization script
# This script sets up Knox Gateway with basic configuration

set -e

echo "Initializing Knox Gateway..."

# Create necessary directories
mkdir -p /opt/knox/data/security/keystores
mkdir -p /opt/knox/logs
mkdir -p /opt/knox/conf/topologies

# Generate keystore if it doesn't exist
if [ ! -f /opt/knox/data/security/keystores/gateway.jks ]; then
    echo "Generating keystore..."
    keytool -genkeypair \
        -alias gateway-identity \
        -keyalg RSA \
        -keysize 2048 \
        -dname "CN=knox, OU=SSB, O=Cloudera, L=San Francisco, ST=CA, C=US" \
        -keypass "admin\r" \
        -keystore /opt/knox/data/security/keystores/gateway.jks \
        -storepass "admin\r" \
        -validity 3650
fi

# Copy topology configuration
if [ -f /opt/knox/conf/ssb.xml ]; then
    cp /opt/knox/conf/ssb.xml /opt/knox/conf/topologies/
    echo "Topology configuration copied."
else
    echo "No topology configuration found, using default."
fi

# Create a simple default topology for testing
cat > /opt/knox/conf/topologies/default.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<topology>
  <gateway>
    <provider>
      <role>authentication</role>
      <name>ShiroProvider</name>
      <enabled>true</enabled>
      <param>
        <name>sessionTimeout</name>
        <value>30</value>
      </param>
      <param>
        <name>urls./**</name>
        <value>authcBasic</value>
      </param>
    </provider>
    <provider>
      <role>identity-assertion</role>
      <name>Default</name>
      <enabled>true</enabled>
    </provider>
    <provider>
      <role>authorization</role>
      <name>AclsAuthz</name>
      <enabled>true</enabled>
    </provider>
  </gateway>
</topology>
EOF
echo "Default topology created."

# Set proper permissions
chown -R knox:knox /opt/knox/data
chown -R knox:knox /opt/knox/logs
chmod 755 /opt/knox/data/security/keystores

echo "Knox Gateway initialization completed."

# Start Knox Gateway
echo "Starting Knox Gateway..."
echo "Checking Knox configuration..."
ls -la /opt/knox/conf/
echo "Checking topology files..."
ls -la /opt/knox/conf/topologies/ || echo "No topologies directory"
echo "Starting gateway with debug output..."
/opt/knox/bin/gateway.sh start 2>&1
