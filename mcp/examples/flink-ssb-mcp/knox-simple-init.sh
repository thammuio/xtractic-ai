#!/bin/bash

# Simple Knox initialization script
set -e

echo "Starting simple Knox initialization..."

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

# Create a minimal topology
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

# Set proper permissions
chown -R knox:knox /opt/knox/data
chown -R knox:knox /opt/knox/logs
chmod 755 /opt/knox/data/security/keystores

echo "Simple Knox initialization completed."

# Try to start Knox
echo "Attempting to start Knox Gateway..."
cd /opt/knox
exec /opt/knox/bin/gateway.sh start
