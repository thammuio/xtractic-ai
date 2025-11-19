from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import anyio

from .config import ServerConfig
from .auth import KnoxAuthFactory
from .client import SMMClient


# Lazy import of MCP to give a clear error if the dependency is missing
try:
    from mcp.server import FastMCP
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "The 'mcp' package is required. Install with: pip install mcp"
    ) from e


def _redact_sensitive(obj: Any, max_items: int = 200) -> Any:
    """Redact common sensitive fields and truncate large collections for LLMs."""
    redact_keys = {
        "password",
        "passcode",
        "token",
        "secret",
        "kerberosKeytab",
        "sslKeystorePasswd",
    }
    if isinstance(obj, dict):
        redacted: Dict[str, Any] = {}
        for k, v in obj.items():
            if k.lower() in redact_keys:
                redacted[k] = "***REDACTED***"
            else:
                redacted[k] = _redact_sensitive(v, max_items)
        return redacted
    if isinstance(obj, list):
        if len(obj) > max_items:
            return [_redact_sensitive(x, max_items) for x in obj[:max_items]] + [
                {"truncated": True, "omitted_count": len(obj) - max_items}
            ]
        return [_redact_sensitive(x, max_items) for x in obj]
    return obj


def _handle_smm_operation(operation_func, *args, **kwargs) -> Dict[str, Any]:
    """Handle SMM operations with proper error handling and redaction."""
    try:
        data = operation_func(*args, **kwargs)
        return _redact_sensitive(data)
    except Exception as e:
        # Return error information in a structured format that Claude can understand
        error_response = {
            "error": True,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "message": f"Operation failed: {str(e)}",
        }
        return error_response


def build_client(config: ServerConfig) -> SMMClient:
    verify = config.build_verify()
    smm_base = config.build_smm_base()

    # Use Knox authentication if Knox is configured, otherwise use direct SMM authentication
    if config.knox_gateway_url:
        auth = KnoxAuthFactory(
            gateway_url=config.knox_gateway_url,
            token=config.knox_token,
            cookie=config.knox_cookie,
            user=config.knox_user,
            password=config.knox_password,
            token_endpoint=config.knox_token_endpoint,
            passcode_token=config.knox_passcode_token,
            verify=verify,
        )
        session = auth.build_session()
    else:
        # Direct SMM authentication
        import requests

        session = requests.Session()
        session.verify = verify
        if config.smm_user and config.smm_password:
            session.auth = (config.smm_user, config.smm_password)

    return SMMClient(
        smm_base,
        session,
        timeout_seconds=config.timeout_seconds,
        proxy_context_path=config.proxy_context_path,
    )


def create_server(smm: SMMClient, readonly: bool) -> FastMCP:
    app = FastMCP("ssm-mcp-server")

    # ============================================================================
    # Core Information Tools
    # ============================================================================

    @app.tool()
    async def get_smm_info() -> Dict[str, Any]:
        """Get SMM version and system information."""
        data = smm.get_smm_info()
        return _redact_sensitive(data)

    @app.tool()
    async def get_smm_version() -> Dict[str, Any]:
        """Get SMM version information."""
        data = smm.get_smm_version()
        return _redact_sensitive(data)

    # ============================================================================
    # Cluster and Broker Management Tools
    # ============================================================================

    @app.tool()
    async def get_cluster_details() -> Dict[str, Any]:
        """Get cluster details and information."""
        return _handle_smm_operation(smm.get_cluster_details)

    @app.tool()
    async def get_brokers() -> Dict[str, Any]:
        """Get all brokers in the cluster."""
        return _handle_smm_operation(smm.get_brokers)

    @app.tool()
    async def get_broker(broker_id: int) -> Dict[str, Any]:
        """Get details of a specific broker."""
        return _handle_smm_operation(smm.get_broker, broker_id)

    @app.tool()
    async def get_broker_metrics(
        broker_id: int,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific broker."""
        return _handle_smm_operation(
            smm.get_broker_metrics, broker_id, duration, from_time, to_time
        )

    @app.tool()
    async def get_all_broker_details() -> Dict[str, Any]:
        """Get all broker details with configurations."""
        return _handle_smm_operation(smm.get_all_broker_details)

    @app.tool()
    async def get_broker_details(broker_id: int) -> Dict[str, Any]:
        """Get detailed broker information including configuration."""
        return _handle_smm_operation(smm.get_broker_details, broker_id)

    # ============================================================================
    # Topic Management Tools
    # ============================================================================

    @app.tool()
    async def get_all_topic_infos() -> Dict[str, Any]:
        """Get all topic information."""
        return _handle_smm_operation(smm.get_all_topic_infos)

    @app.tool()
    async def get_topic_description(topic_name: str) -> Dict[str, Any]:
        """Get detailed description of a specific topic."""
        return _handle_smm_operation(smm.get_topic_description, topic_name)

    @app.tool()
    async def get_topic_info(topic_name: str) -> Dict[str, Any]:
        """Get basic information about a specific topic."""
        return _handle_smm_operation(smm.get_topic_info, topic_name)

    @app.tool()
    async def get_topic_partitions(topic_name: str) -> Dict[str, Any]:
        """Get partition information for a specific topic."""
        return _handle_smm_operation(smm.get_topic_partitions, topic_name)

    @app.tool()
    async def get_topic_partition_infos(topic_name: str) -> Dict[str, Any]:
        """Get detailed partition information for a specific topic."""
        return _handle_smm_operation(smm.get_topic_partition_infos, topic_name)

    @app.tool()
    async def get_topic_configs(topic_name: str) -> Dict[str, Any]:
        """Get configuration for a specific topic."""
        return _handle_smm_operation(smm.get_topic_configs, topic_name)

    @app.tool()
    async def get_all_topic_configs() -> Dict[str, Any]:
        """Get configurations for all topics."""
        return _handle_smm_operation(smm.get_all_topic_configs)

    @app.tool()
    async def get_default_topic_configs() -> Dict[str, Any]:
        """Get default topic configurations."""
        return _handle_smm_operation(smm.get_default_topic_configs)

    @app.tool()
    async def get_topic_offsets(topic_name: str) -> Dict[str, Any]:
        """Get offset information for a topic."""
        return _handle_smm_operation(smm.get_topic_offsets, topic_name)

    @app.tool()
    async def get_topic_content(
        topic_name: str, partition: int, offset: int, limit: int = 10
    ) -> Dict[str, Any]:
        """Get content from a topic partition."""
        return _handle_smm_operation(
            smm.get_topic_content, topic_name, partition, offset, limit
        )

    # Write operations (only available if not in readonly mode)
    if not readonly:

        @app.tool()
        async def create_topics(topics_config: List[Dict[str, Any]]) -> Dict[str, Any]:
            """Create new topics."""
            return _handle_smm_operation(smm.create_topics, topics_config)

        @app.tool()
        async def create_partitions(
            topic_name: str, partition_count: int
        ) -> Dict[str, Any]:
            """Create additional partitions for a topic."""
            return _handle_smm_operation(
                smm.create_partitions, topic_name, partition_count
            )

        @app.tool()
        async def delete_topics(topic_names: List[str]) -> Dict[str, Any]:
            """Delete specified topics."""
            return _handle_smm_operation(smm.delete_topics, topic_names)

        @app.tool()
        async def alter_topic_configs(
            topic_name: str, configs: Dict[str, str]
        ) -> Dict[str, Any]:
            """Alter topic configurations."""
            return _handle_smm_operation(smm.alter_topic_configs, topic_name, configs)

    # ============================================================================
    # Consumer Group Management Tools
    # ============================================================================

    @app.tool()
    async def get_consumer_groups() -> Dict[str, Any]:
        """Get all consumer groups."""
        return _handle_smm_operation(smm.get_consumer_groups)

    @app.tool()
    async def get_consumer_group_names() -> Dict[str, Any]:
        """Get all consumer group names."""
        return _handle_smm_operation(smm.get_consumer_group_names)

    @app.tool()
    async def get_consumer_group_info(group_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific consumer group."""
        return _handle_smm_operation(smm.get_consumer_group_info, group_name)

    @app.tool()
    async def get_all_consumer_info() -> Dict[str, Any]:
        """Get information about all consumers."""
        return _handle_smm_operation(smm.get_all_consumer_info)

    @app.tool()
    async def get_consumer_info(consumer_id: str) -> Dict[str, Any]:
        """Get information about a specific consumer."""
        return _handle_smm_operation(smm.get_consumer_info, consumer_id)

    @app.tool()
    async def reset_offset(
        group_name: str, topic_name: str, partition: int, offset: int
    ) -> Dict[str, Any]:
        """Reset consumer group offset."""
        return _handle_smm_operation(
            smm.reset_offset, group_name, topic_name, partition, offset
        )

    # ============================================================================
    # Metrics and Monitoring Tools
    # ============================================================================

    @app.tool()
    async def get_cluster_with_broker_metrics(
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get cluster metrics including broker metrics."""
        return _handle_smm_operation(
            smm.get_cluster_with_broker_metrics, duration, from_time, to_time
        )

    @app.tool()
    async def get_cluster_with_topic_metrics(
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get cluster metrics including topic metrics."""
        return _handle_smm_operation(
            smm.get_cluster_with_topic_metrics, duration, from_time, to_time
        )

    @app.tool()
    async def get_all_consumer_group_metrics(
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        state: Optional[str] = None,
        include_producer_metrics: bool = False,
        include_assignments: bool = False,
    ) -> Dict[str, Any]:
        """Get metrics for all consumer groups."""
        return _handle_smm_operation(
            smm.get_all_consumer_group_metrics,
            duration,
            from_time,
            to_time,
            state,
            include_producer_metrics,
            include_assignments,
        )

    @app.tool()
    async def get_consumer_group_metrics(
        group_name: str,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific consumer group."""
        return _handle_smm_operation(
            smm.get_consumer_group_metrics, group_name, duration, from_time, to_time
        )

    @app.tool()
    async def get_all_producer_metrics(
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for all producers."""
        return _handle_smm_operation(
            smm.get_all_producer_metrics, duration, from_time, to_time
        )

    @app.tool()
    async def get_producer_metrics(
        producer_id: str,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific producer."""
        return _handle_smm_operation(
            smm.get_producer_metrics, producer_id, duration, from_time, to_time
        )

    @app.tool()
    async def get_topic_metrics(
        topic_name: str,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific topic."""
        return _handle_smm_operation(
            smm.get_topic_metrics, topic_name, duration, from_time, to_time
        )

    @app.tool()
    async def get_topic_partition_metrics(
        topic_name: str,
        partition_num: int,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific topic partition."""
        return _handle_smm_operation(
            smm.get_topic_partition_metrics,
            topic_name,
            partition_num,
            duration,
            from_time,
            to_time,
        )

    # ============================================================================
    # Alert Management Tools
    # ============================================================================

    @app.tool()
    async def get_all_alert_policies() -> Dict[str, Any]:
        """Get all alert policies."""
        return _handle_smm_operation(smm.get_all_alert_policies)

    @app.tool()
    async def get_alert_policy(policy_id: str) -> Dict[str, Any]:
        """Get details of a specific alert policy."""
        return _handle_smm_operation(smm.get_alert_policy, policy_id)

    @app.tool()
    async def get_alert_notifications() -> Dict[str, Any]:
        """Get all alert notifications."""
        return _handle_smm_operation(smm.get_alert_notifications)

    @app.tool()
    async def get_alert_notifications_by_entity_type(
        entity_type: str,
    ) -> Dict[str, Any]:
        """Get alert notifications by entity type."""
        return _handle_smm_operation(
            smm.get_alert_notifications_by_entity_type, entity_type
        )

    @app.tool()
    async def get_alert_notifications_by_entity_type_and_name(
        entity_type: str, entity_name: str
    ) -> Dict[str, Any]:
        """Get alert notifications by entity type and name."""
        return _handle_smm_operation(
            smm.get_alert_notifications_by_entity_type_and_name,
            entity_type,
            entity_name,
        )

    # Write operations for alerts (only available if not in readonly mode)
    if not readonly:

        @app.tool()
        async def add_alert_policy(policy_config: Dict[str, Any]) -> Dict[str, Any]:
            """Add a new alert policy."""
            return _handle_smm_operation(smm.add_alert_policy, policy_config)

        @app.tool()
        async def update_alert_policy(
            policy_id: str, policy_config: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Update an existing alert policy."""
            return _handle_smm_operation(
                smm.update_alert_policy, policy_id, policy_config
            )

        @app.tool()
        async def delete_alert_policy(policy_id: str) -> Dict[str, Any]:
            """Delete an alert policy."""
            return _handle_smm_operation(smm.delete_alert_policy, policy_id)

        @app.tool()
        async def enable_alert_policy(policy_id: str) -> Dict[str, Any]:
            """Enable an alert policy."""
            return _handle_smm_operation(smm.enable_alert_policy, policy_id)

        @app.tool()
        async def disable_alert_policy(policy_id: str) -> Dict[str, Any]:
            """Disable an alert policy."""
            return _handle_smm_operation(smm.disable_alert_policy, policy_id)

        @app.tool()
        async def mark_alert_notifications(
            notification_ids: List[str],
        ) -> Dict[str, Any]:
            """Mark alert notifications as read."""
            return _handle_smm_operation(smm.mark_alert_notifications, notification_ids)

        @app.tool()
        async def unmark_alert_notifications(
            notification_ids: List[str],
        ) -> Dict[str, Any]:
            """Unmark alert notifications as unread."""
            return _handle_smm_operation(
                smm.unmark_alert_notifications, notification_ids
            )

    # ============================================================================
    # Schema Registry Tools
    # ============================================================================

    @app.tool()
    async def get_schema_registry_info() -> Dict[str, Any]:
        """Get schema registry information."""
        return _handle_smm_operation(smm.get_schema_registry_info)

    @app.tool()
    async def get_schema_meta_for_topic(topic_name: str) -> Dict[str, Any]:
        """Get schema metadata for a specific topic."""
        return _handle_smm_operation(smm.get_schema_meta_for_topic, topic_name)

    @app.tool()
    async def get_key_schema_version_infos(topic_name: str) -> Dict[str, Any]:
        """Get key schema version information for a topic."""
        return _handle_smm_operation(smm.get_key_schema_version_infos, topic_name)

    @app.tool()
    async def get_value_schema_version_infos(topic_name: str) -> Dict[str, Any]:
        """Get value schema version information for a topic."""
        return _handle_smm_operation(smm.get_value_schema_version_infos, topic_name)

    # Write operations for schema registry (only available if not in readonly mode)
    if not readonly:

        @app.tool()
        async def register_topic_schema_meta(
            topic_name: str, schema_config: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Register schema metadata for a topic."""
            return _handle_smm_operation(
                smm.register_topic_schema_meta, topic_name, schema_config
            )

    # ============================================================================
    # Kafka Connect Tools
    # ============================================================================

    @app.tool()
    async def get_connectors() -> Dict[str, Any]:
        """Get all Kafka Connect connectors."""
        return _handle_smm_operation(smm.get_connectors)

    @app.tool()
    async def get_connector(connector_name: str) -> Dict[str, Any]:
        """Get details of a specific connector."""
        return _handle_smm_operation(smm.get_connector, connector_name)

    @app.tool()
    async def get_connector_config_def(connector_name: str) -> Dict[str, Any]:
        """Get connector configuration definition."""
        return _handle_smm_operation(smm.get_connector_config_def, connector_name)

    @app.tool()
    async def get_connector_permissions(connector_name: str) -> Dict[str, Any]:
        """Get connector permissions."""
        return _handle_smm_operation(smm.get_connector_permissions, connector_name)

    @app.tool()
    async def get_connect_worker_metrics(
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Kafka Connect worker metrics."""
        return _handle_smm_operation(
            smm.get_connect_worker_metrics, duration, from_time, to_time
        )

    # Write operations for Kafka Connect (only available if not in readonly mode)
    if not readonly:

        @app.tool()
        async def create_connector(connector_config: Dict[str, Any]) -> Dict[str, Any]:
            """Create a new connector."""
            return _handle_smm_operation(smm.create_connector, connector_config)

        @app.tool()
        async def delete_connector(connector_name: str) -> Dict[str, Any]:
            """Delete a connector."""
            return _handle_smm_operation(smm.delete_connector, connector_name)

        @app.tool()
        async def configure_connector(
            connector_name: str, config: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Configure a connector."""
            return _handle_smm_operation(
                smm.configure_connector, connector_name, config
            )

    # ============================================================================
    # Lineage Tools
    # ============================================================================

    @app.tool()
    async def get_topic_lineage(topic_name: str) -> Dict[str, Any]:
        """Get lineage information for a topic."""
        return _handle_smm_operation(smm.get_topic_lineage, topic_name)

    @app.tool()
    async def get_topic_partition_lineage(
        topic_name: str, partition: int
    ) -> Dict[str, Any]:
        """Get lineage information for a topic partition."""
        return _handle_smm_operation(
            smm.get_topic_partition_lineage, topic_name, partition
        )

    @app.tool()
    async def get_consumer_group_lineage(group_name: str) -> Dict[str, Any]:
        """Get lineage information for a consumer group."""
        return _handle_smm_operation(smm.get_consumer_group_lineage, group_name)

    @app.tool()
    async def get_producer_lineage(producer_id: str) -> Dict[str, Any]:
        """Get lineage information for a producer."""
        return _handle_smm_operation(smm.get_producer_lineage, producer_id)

    # ============================================================================
    # Authentication Tools
    # ============================================================================

    @app.tool()
    async def get_access() -> Dict[str, Any]:
        """Get access information."""
        return _handle_smm_operation(smm.get_access)

    # Write operations for authentication (only available if not in readonly mode)
    if not readonly:

        @app.tool()
        async def login(username: str, password: str) -> Dict[str, Any]:
            """Login to SMM."""
            return _handle_smm_operation(smm.login, username, password)

        @app.tool()
        async def logout() -> Dict[str, Any]:
            """Logout from SMM."""
            return _handle_smm_operation(smm.logout)

    # ============================================================================
    # Phase 1: High Priority New Tools
    # ============================================================================

    # Alert Management Completion
    @app.tool()
    async def disable_alert_policy(policy_id: str) -> Dict[str, Any]:
        """Disable an alert policy."""
        return _handle_smm_operation(smm.disable_alert_policy, policy_id)

    @app.tool()
    async def enable_alert_policy(policy_id: str) -> Dict[str, Any]:
        """Enable an alert policy."""
        return _handle_smm_operation(smm.enable_alert_policy, policy_id)

    @app.tool()
    async def get_alert_policy_automata(policy_id: str) -> Dict[str, Any]:
        """Get alert policy automata details."""
        return _handle_smm_operation(smm.get_alert_policy_automata, policy_id)

    @app.tool()
    async def get_alert_notifications_by_entity(entity_type: str, entity_id: str) -> Dict[str, Any]:
        """Get alert notifications by entity type and ID."""
        return _handle_smm_operation(smm.get_alert_notifications_by_entity, entity_type, entity_id)

    @app.tool()
    async def mark_alert_notifications_read(notification_ids: List[str]) -> Dict[str, Any]:
        """Mark alert notifications as read."""
        return _handle_smm_operation(smm.mark_alert_notifications_read, notification_ids)

    # Notifiers Management
    @app.tool()
    async def get_notifiers() -> Dict[str, Any]:
        """Get all notifiers."""
        return _handle_smm_operation(smm.get_notifiers)

    @app.tool()
    async def get_notifier(notifier_id: str) -> Dict[str, Any]:
        """Get specific notifier details."""
        return _handle_smm_operation(smm.get_notifier, notifier_id)

    @app.tool()
    async def get_notifier_provider_configs() -> Dict[str, Any]:
        """Get notifier provider configurations."""
        return _handle_smm_operation(smm.get_notifier_provider_configs)

    # End-to-End Latency Monitoring
    @app.tool()
    async def get_topic_etelatency(
        topic_name: str, 
        duration: Optional[str] = None, 
        from_time: Optional[str] = None, 
        to_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get end-to-end latency for a topic."""
        return _handle_smm_operation(smm.get_topic_etelatency, topic_name, duration, from_time, to_time)

    @app.tool()
    async def get_topic_group_etelatency(
        topic_name: str, 
        group_name: str, 
        duration: Optional[str] = None, 
        from_time: Optional[str] = None, 
        to_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get end-to-end latency for topic and consumer group."""
        return _handle_smm_operation(smm.get_topic_group_etelatency, topic_name, group_name, duration, from_time, to_time)

    # Replication Statistics
    @app.tool()
    async def get_replication_stats() -> Dict[str, Any]:
        """Get replication statistics."""
        return _handle_smm_operation(smm.get_replication_stats)

    @app.tool()
    async def is_replication_configured() -> Dict[str, Any]:
        """Check if replication is configured."""
        return _handle_smm_operation(smm.is_replication_configured)

    @app.tool()
    async def get_replication_stats_by_cluster(source: str, target: str) -> Dict[str, Any]:
        """Get replication stats by source and target clusters."""
        return _handle_smm_operation(smm.get_replication_stats_by_cluster, source, target)

    @app.tool()
    async def get_topic_replication_stats(source: str, target: str, topic_name: str) -> Dict[str, Any]:
        """Get replication stats for specific topic."""
        return _handle_smm_operation(smm.get_topic_replication_stats, source, target, topic_name)

    @app.tool()
    async def get_topic_replication_stats_simple(topic_name: str) -> Dict[str, Any]:
        """Get simple replication stats for topic."""
        return _handle_smm_operation(smm.get_topic_replication_stats_simple, topic_name)

    # Kafka Connect Enhancements
    @app.tool()
    async def get_connector_templates() -> Dict[str, Any]:
        """Get available connector templates."""
        return _handle_smm_operation(smm.get_connector_templates)

    @app.tool()
    async def get_connector_config_definitions(connector_plugin_class: str) -> Dict[str, Any]:
        """Get connector configuration definitions."""
        return _handle_smm_operation(smm.get_connector_config_definitions, connector_plugin_class)

    @app.tool()
    async def get_connector_config_sample(name: str, connector_plugin_class: str, version: str) -> Dict[str, Any]:
        """Get sample connector configuration."""
        return _handle_smm_operation(smm.get_connector_config_sample, name, connector_plugin_class, version)

    @app.tool()
    async def validate_connector_config(config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate connector configuration."""
        return _handle_smm_operation(smm.validate_connector_config, config)

    @app.tool()
    async def perform_connector_action(connector_name: str, action: str) -> Dict[str, Any]:
        """Perform connector actions (start, stop, restart, etc.)."""
        return _handle_smm_operation(smm.perform_connector_action, connector_name, action)

    @app.tool()
    async def is_connect_configured() -> Dict[str, Any]:
        """Check if Kafka Connect is configured."""
        return _handle_smm_operation(smm.is_connect_configured)

    @app.tool()
    async def get_connector_sink_metrics(connector_name: str) -> Dict[str, Any]:
        """Get connector sink metrics."""
        return _handle_smm_operation(smm.get_connector_sink_metrics, connector_name)

    @app.tool()
    async def get_connect_worker_metrics(
        duration: Optional[str] = None, 
        from_time: Optional[str] = None, 
        to_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get Kafka Connect worker metrics."""
        return _handle_smm_operation(smm.get_connect_worker_metrics, duration, from_time, to_time)

    return app


async def run_stdio() -> None:
    # For FastMCP, prefer the built-in stdio runner
    config = ServerConfig()
    smm = build_client(config)
    server = create_server(smm, readonly=config.readonly)
    # run() is synchronous; call the async flavor directly
    await server.run_stdio_async()


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    if transport != "stdio":
        # Defer to FastMCP synchronous run helper for other transports when added
        config = ServerConfig()
        smm = build_client(config)
        server = create_server(smm, readonly=config.readonly)
        server.run(transport=transport)
        return
    anyio.run(run_stdio)


if __name__ == "__main__":
    main()
