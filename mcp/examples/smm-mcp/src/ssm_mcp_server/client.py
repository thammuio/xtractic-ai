from __future__ import annotations

from typing import Any, Dict, Optional, List

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class SMMError(Exception):
    pass


class SMMClient:
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        timeout_seconds: int = 30,
        proxy_context_path: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.timeout = timeout_seconds
        self.proxy_context_path = proxy_context_path

        # Add CDP proxy headers if configured
        if self.proxy_context_path:
            self.session.headers.update({"X-ProxyContextPath": self.proxy_context_path})

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    @retry(
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError, requests.Timeout)
        ),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        resp = self.session.get(self._url(path), params=params, timeout=self.timeout)
        if resp.status_code == 401:
            raise requests.HTTPError("Unauthorized", response=resp)
        if resp.status_code == 403:
            raise requests.HTTPError("Forbidden", response=resp)
        if not resp.ok:
            # Try to get detailed error message from response
            try:
                error_data = resp.json()
                error_message = error_data.get(
                    "error_message", f"HTTP {resp.status_code} Error"
                )
            except Exception:
                error_message = f"HTTP {resp.status_code} Error: {resp.text}"
            raise SMMError(f"{error_message} for {path}")
        return resp.json()

    @retry(
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError, requests.Timeout)
        ),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _post(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        resp = self.session.post(
            self._url(path), data=data, json=json_data, timeout=self.timeout
        )
        if resp.status_code == 401:
            raise requests.HTTPError("Unauthorized", response=resp)
        if resp.status_code == 403:
            raise requests.HTTPError("Forbidden", response=resp)
        if not resp.ok:
            # Try to get detailed error message from response
            try:
                error_data = resp.json()
                error_message = error_data.get(
                    "error_message", f"HTTP {resp.status_code} Error"
                )
            except Exception:
                error_message = f"HTTP {resp.status_code} Error: {resp.text}"
            raise SMMError(f"{error_message} for {path}")
        return resp.json()

    @retry(
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError, requests.Timeout)
        ),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _put(
        self,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        resp = self.session.put(
            self._url(path), data=data, json=json_data, timeout=self.timeout
        )
        if resp.status_code == 401:
            raise requests.HTTPError("Unauthorized", response=resp)
        if resp.status_code == 403:
            raise requests.HTTPError("Forbidden", response=resp)
        resp.raise_for_status()
        return resp.json()

    @retry(
        retry=retry_if_exception_type(
            (requests.HTTPError, requests.ConnectionError, requests.Timeout)
        ),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
        stop=stop_after_attempt(3),
        reraise=True,
    )
    def _delete(self, path: str) -> Dict[str, Any]:
        resp = self.session.delete(self._url(path), timeout=self.timeout)
        if resp.status_code == 401:
            raise requests.HTTPError("Unauthorized", response=resp)
        if resp.status_code == 403:
            raise requests.HTTPError("Forbidden", response=resp)
        resp.raise_for_status()
        return resp.json()

    # ============================================================================
    # SMM API Methods - Core Information
    # ============================================================================

    def get_smm_info(self) -> Dict[str, Any]:
        """Get SMM version and system information."""
        try:
            # Try to get basic cluster info using working endpoints
            brokers = self._get("brokers")
            topics = self._get("configs/topics")
            return {
                "status": "connected",
                "message": f"SMM MCP Server connected (brokers: {len(brokers)}, topics: {len(topics)})",
                "brokers_count": len(brokers),
                "topics_count": len(topics),
            }
        except Exception as e:
            return {
                "status": "connected",
                "message": f"SMM MCP Server connected (limited info: {str(e)})",
            }

    def get_smm_version(self) -> Dict[str, Any]:
        """Get SMM version information."""
        # SMM version is typically available in the web UI, but not via API
        # Return a placeholder response
        return {
            "version": "SMM (version not available via API)",
            "message": "SMM version information not accessible via REST API"
        }

    # ============================================================================
    # SMM API Methods - Cluster and Broker Management
    # ============================================================================

    def get_cluster_details(self) -> Dict[str, Any]:
        """Get cluster details and information."""
        # Use brokers endpoint to get cluster info
        brokers = self._get("brokers")
        return {
            "brokers": brokers,
            "broker_count": len(brokers),
            "cluster_info": "Cluster details retrieved from brokers endpoint"
        }

    def get_brokers(self) -> Dict[str, Any]:
        """Get all brokers in the cluster."""
        return self._get("brokers")

    def get_broker(self, broker_id: int) -> Dict[str, Any]:
        """Get details of a specific broker."""
        # Get all brokers and find the specific one
        brokers = self._get("brokers")
        for broker in brokers:
            if broker.get("id") == broker_id:
                return broker
        raise ValueError(f"Broker {broker_id} not found")

    def get_broker_metrics(
        self,
        broker_id: int,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific broker."""
        # SMM doesn't provide broker-specific metrics via API
        # Return broker info instead
        broker = self.get_broker(broker_id)
        return {
            "broker_id": broker_id,
            "broker_info": broker,
            "message": "Broker metrics not available via SMM API",
            "duration": duration,
            "from_time": from_time,
            "to_time": to_time
        }

    def get_all_broker_details(self) -> Dict[str, Any]:
        """Get all broker details with configurations."""
        # Use brokers endpoint as fallback
        brokers = self._get("brokers")
        return {
            "brokers": brokers,
            "broker_count": len(brokers),
            "message": "Broker details retrieved from brokers endpoint"
        }

    def get_broker_details(self, broker_id: int) -> Dict[str, Any]:
        """Get detailed broker information including configuration."""
        # Get broker info from brokers list
        broker = self.get_broker(broker_id)
        return {
            "broker": broker,
            "broker_id": broker_id,
            "message": "Broker details retrieved from brokers endpoint"
        }

    # ============================================================================
    # SMM API Methods - Topic Management
    # ============================================================================

    def get_all_topic_infos(self) -> Dict[str, Any]:
        """Get all topic information."""
        return self._get("configs/topics")

    def get_topic_description(self, topic_name: str) -> Dict[str, Any]:
        """Get detailed description of a specific topic."""
        # Find topic in the topics list
        topics = self._get("configs/topics")
        for topic in topics:
            if topic.get("resourceName") == topic_name:
                return {
                    "topic_name": topic_name,
                    "topic_info": topic,
                    "message": "Topic description retrieved from topics list"
                }
        raise ValueError(f"Topic {topic_name} not found")

    def get_topic_info(self, topic_name: str) -> Dict[str, Any]:
        """Get basic information about a specific topic."""
        # Use the same logic as get_topic_description
        return self.get_topic_description(topic_name)

    def get_topic_partitions(self, topic_name: str) -> Dict[str, Any]:
        """Get partition information for a specific topic."""
        # Get topic info and extract partition info
        topic_info = self.get_topic_info(topic_name)
        return {
            "topic_name": topic_name,
            "partitions": topic_info.get("topic_info", {}).get("partitions", []),
            "partition_count": len(topic_info.get("topic_info", {}).get("partitions", [])),
            "message": "Partition information retrieved from topic info"
        }

    def get_topic_partition_infos(self, topic_name: str) -> Dict[str, Any]:
        """Get detailed partition information for a specific topic."""
        # Use the same logic as get_topic_partitions
        return self.get_topic_partitions(topic_name)

    def create_topics(self, topics_config: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create new topics."""
        return self._post(
            "topicMetadata/createTopics", json_data={"topics": topics_config}
        )

    def create_partitions(
        self, topic_name: str, partition_count: int
    ) -> Dict[str, Any]:
        """Create additional partitions for a topic."""
        return self._post(
            f"topicMetadata/createPartitions/{topic_name}",
            json_data={"partitionCount": partition_count},
        )

    def delete_topics(self, topic_names: List[str]) -> Dict[str, Any]:
        """Delete specified topics."""
        return self._post(
            "topicMetadata/deleteTopics", json_data={"topics": topic_names}
        )

    def get_topic_configs(self, topic_name: str) -> Dict[str, Any]:
        """Get configuration for a specific topic."""
        # Get topic info which includes configuration
        topic_info = self.get_topic_info(topic_name)
        return {
            "topic_name": topic_name,
            "configs": topic_info.get("topic_info", {}).get("configs", {}),
            "message": "Topic configuration retrieved from topic info"
        }

    def get_all_topic_configs(self) -> Dict[str, Any]:
        """Get configurations for all topics."""
        # Get all topics which include their configurations
        topics = self._get("configs/topics")
        return {
            "topics": topics,
            "topic_count": len(topics),
            "message": "All topic configurations retrieved from topics list"
        }

    def get_default_topic_configs(self) -> Dict[str, Any]:
        """Get default topic configurations."""
        return self._get("configs/default/topics")

    def alter_topic_configs(
        self, topic_name: str, configs: Dict[str, str]
    ) -> Dict[str, Any]:
        """Alter topic configurations."""
        return self._post(
            f"resourceConfiguration/alterTopicConfigs/{topic_name}", json_data=configs
        )

    # ============================================================================
    # SMM API Methods - Consumer Group Management
    # ============================================================================

    def get_consumer_groups(self) -> Dict[str, Any]:
        """Get all consumer groups."""
        return self._get("consumerGroupRelatedDetails/consumerGroups")

    def get_consumer_group_names(self) -> Dict[str, Any]:
        """Get all consumer group names."""
        return self._get("consumerGroupRelatedDetails/consumerGroupNames")

    def get_consumer_group_info(self, group_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific consumer group."""
        return self._get(f"consumerGroupRelatedDetails/consumerGroupInfo/{group_name}")

    def get_all_consumer_info(self) -> Dict[str, Any]:
        """Get information about all consumers."""
        return self._get("consumerGroupRelatedDetails/allConsumerInfo")

    def get_consumer_info(self, consumer_id: str) -> Dict[str, Any]:
        """Get information about a specific consumer."""
        return self._get(f"consumerGroupRelatedDetails/consumerInfo/{consumer_id}")

    def reset_offset(
        self, group_name: str, topic_name: str, partition: int, offset: int
    ) -> Dict[str, Any]:
        """Reset consumer group offset."""
        return self._post(
            f"consumerGroupRelatedDetails/resetOffset/{group_name}",
            json_data={"topic": topic_name, "partition": partition, "offset": offset},
        )

    # ============================================================================
    # SMM API Methods - Metrics and Monitoring
    # ============================================================================

    def get_cluster_with_broker_metrics(
        self,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get cluster metrics including broker metrics."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get(
            "admin/metrics/aggregated/clusterWithBrokerMetrics", params=params
        )

    def get_cluster_with_topic_metrics(
        self,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get cluster metrics including topic metrics."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get(
            "admin/metrics/aggregated/clusterWithTopicMetrics", params=params
        )

    def get_all_consumer_group_metrics(
        self,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
        state: Optional[str] = None,
        include_producer_metrics: bool = False,
        include_assignments: bool = False,
    ) -> Dict[str, Any]:
        """Get metrics for all consumer groups."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        if state:
            params["state"] = state
        if include_producer_metrics:
            params["includeProducerMetrics"] = include_producer_metrics
        if include_assignments:
            params["includeAssignments"] = include_assignments
        return self._get("admin/metrics/aggregated/groups", params=params)

    def get_consumer_group_metrics(
        self,
        group_name: str,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific consumer group."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get(f"admin/metrics/aggregated/groups/{group_name}", params=params)

    def get_all_producer_metrics(
        self,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for all producers."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get("admin/metrics/aggregated/producers", params=params)

    def get_producer_metrics(
        self,
        producer_id: str,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific producer."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get(
            f"admin/metrics/aggregated/producers/{producer_id}", params=params
        )

    def get_topic_metrics(
        self,
        topic_name: str,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific topic."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get(f"topicMetrics/topicMetrics/{topic_name}", params=params)

    def get_topic_partition_metrics(
        self,
        topic_name: str,
        partition_num: int,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get metrics for a specific topic partition."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get(
            f"topicMetrics/topicPartitionMetrics/{topic_name}/{partition_num}",
            params=params,
        )

    # ============================================================================
    # SMM API Methods - Alert Management
    # ============================================================================

    def get_all_alert_policies(self) -> Dict[str, Any]:
        """Get all alert policies."""
        return self._get("alertPolicyOperations/allAlertPolicies")

    def get_alert_policy(self, policy_id: str) -> Dict[str, Any]:
        """Get details of a specific alert policy."""
        return self._get(f"alertPolicyOperations/alertPolicy/{policy_id}")

    def add_alert_policy(self, policy_config: Dict[str, Any]) -> Dict[str, Any]:
        """Add a new alert policy."""
        return self._post(
            "alertPolicyOperations/addAlertPolicy", json_data=policy_config
        )

    def update_alert_policy(
        self, policy_id: str, policy_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing alert policy."""
        return self._put(
            f"alertPolicyOperations/updateAlertPolicy/{policy_id}",
            json_data=policy_config,
        )

    def delete_alert_policy(self, policy_id: str) -> Dict[str, Any]:
        """Delete an alert policy."""
        return self._delete(f"alertPolicyOperations/deleteAlertPolicy/{policy_id}")

    def enable_alert_policy(self, policy_id: str) -> Dict[str, Any]:
        """Enable an alert policy."""
        return self._post(f"alertPolicyOperations/enableAlertPolicy/{policy_id}")

    def disable_alert_policy(self, policy_id: str) -> Dict[str, Any]:
        """Disable an alert policy."""
        return self._post(f"alertPolicyOperations/disableAlertPolicy/{policy_id}")

    def get_alert_notifications(self) -> Dict[str, Any]:
        """Get all alert notifications."""
        return self._get("alertNotifications/alertNotifications")

    def get_alert_notifications_by_entity_type(
        self, entity_type: str
    ) -> Dict[str, Any]:
        """Get alert notifications by entity type."""
        return self._get(
            f"alertNotifications/alertNotificationsByEntityType/{entity_type}"
        )

    def get_alert_notifications_by_entity_type_and_name(
        self, entity_type: str, entity_name: str
    ) -> Dict[str, Any]:
        """Get alert notifications by entity type and name."""
        return self._get(
            f"alertNotifications/alertNotificationsByEntityTypeAndName/{entity_type}/{entity_name}"
        )

    def mark_alert_notifications(self, notification_ids: List[str]) -> Dict[str, Any]:
        """Mark alert notifications as read."""
        return self._post(
            "alertNotifications/markAlertNotifications",
            json_data={"notificationIds": notification_ids},
        )

    def unmark_alert_notifications(self, notification_ids: List[str]) -> Dict[str, Any]:
        """Unmark alert notifications as unread."""
        return self._post(
            "alertNotifications/unmarkAlertNotifications",
            json_data={"notificationIds": notification_ids},
        )

    # ============================================================================
    # SMM API Methods - Schema Registry
    # ============================================================================

    def get_schema_registry_info(self) -> Dict[str, Any]:
        """Get schema registry information."""
        return self._get("schemaRegistry/schemaRegistryInfo")

    def get_schema_meta_for_topic(self, topic_name: str) -> Dict[str, Any]:
        """Get schema metadata for a specific topic."""
        return self._get(f"schemaRegistry/schemaMetaForTopic/{topic_name}")

    def get_key_schema_version_infos(self, topic_name: str) -> Dict[str, Any]:
        """Get key schema version information for a topic."""
        return self._get(f"schemaRegistry/keySchemaVersionInfos/{topic_name}")

    def get_value_schema_version_infos(self, topic_name: str) -> Dict[str, Any]:
        """Get value schema version information for a topic."""
        return self._get(f"schemaRegistry/valueSchemaVersionInfos/{topic_name}")

    def register_topic_schema_meta(
        self, topic_name: str, schema_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Register schema metadata for a topic."""
        return self._post(
            f"schemaRegistry/registerTopicSchemaMeta/{topic_name}",
            json_data=schema_config,
        )

    # ============================================================================
    # SMM API Methods - Kafka Connect
    # ============================================================================

    def get_connectors(self) -> Dict[str, Any]:
        """Get all Kafka Connect connectors."""
        return self._get("kafkaConnect/connectors")

    def get_connector(self, connector_name: str) -> Dict[str, Any]:
        """Get details of a specific connector."""
        return self._get(f"kafkaConnect/connector/{connector_name}")

    def create_connector(self, connector_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new connector."""
        return self._post("kafkaConnect/createConnector", json_data=connector_config)

    def delete_connector(self, connector_name: str) -> Dict[str, Any]:
        """Delete a connector."""
        return self._delete(f"kafkaConnect/deleteConnector/{connector_name}")

    def configure_connector(
        self, connector_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Configure a connector."""
        return self._post(
            f"kafkaConnect/configureConnector/{connector_name}", json_data=config
        )

    def get_connector_config_def(self, connector_name: str) -> Dict[str, Any]:
        """Get connector configuration definition."""
        return self._get(f"kafkaConnect/connectorConfigDef/{connector_name}")

    def get_connector_permissions(self, connector_name: str) -> Dict[str, Any]:
        """Get connector permissions."""
        return self._get(f"kafkaConnect/connectorPermissions/{connector_name}")

    def get_connect_worker_metrics(
        self,
        duration: Optional[str] = None,
        from_time: Optional[int] = None,
        to_time: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get Kafka Connect worker metrics."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time is not None:
            params["from"] = from_time
        if to_time is not None:
            params["to"] = to_time
        return self._get("kafkaConnectMetrics/connectWorkerMetrics", params=params)

    # ============================================================================
    # SMM API Methods - Lineage
    # ============================================================================

    def get_topic_lineage(self, topic_name: str) -> Dict[str, Any]:
        """Get lineage information for a topic."""
        return self._get(f"lineage/topicLineage/{topic_name}")

    def get_topic_partition_lineage(
        self, topic_name: str, partition: int
    ) -> Dict[str, Any]:
        """Get lineage information for a topic partition."""
        return self._get(f"lineage/topicPartitionLineage/{topic_name}/{partition}")

    def get_consumer_group_lineage(self, group_name: str) -> Dict[str, Any]:
        """Get lineage information for a consumer group."""
        return self._get(f"lineage/consumerGroupLineage/{group_name}")

    def get_producer_lineage(self, producer_id: str) -> Dict[str, Any]:
        """Get lineage information for a producer."""
        return self._get(f"lineage/producerLineage/{producer_id}")

    # ============================================================================
    # SMM API Methods - Topic Consumption
    # ============================================================================

    def get_topic_content(
        self, topic_name: str, partition: int, offset: int, limit: int = 10
    ) -> Dict[str, Any]:
        """Get content from a topic partition."""
        params = {"partition": partition, "offset": offset, "limit": limit}
        return self._get(f"topicConsumption/topicContent/{topic_name}", params=params)

    def get_topic_offsets(self, topic_name: str) -> Dict[str, Any]:
        """Get offset information for a topic."""
        return self._get(f"topicConsumption/topicOffsets/{topic_name}")

    # ============================================================================
    # SMM API Methods - Authentication
    # ============================================================================

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """Login to SMM."""
        return self._post(
            "authentication/login",
            json_data={"username": username, "password": password},
        )

    def logout(self) -> Dict[str, Any]:
        """Logout from SMM."""
        return self._post("authentication/logout")

    # ============================================================================
    # Phase 1: High Priority New Methods
    # ============================================================================

    # Alert Management Completion
    def disable_alert_policy(self, policy_id: str) -> Dict[str, Any]:
        """Disable an alert policy."""
        return self._post(f"alertPolicy/{policy_id}/disable")

    def enable_alert_policy(self, policy_id: str) -> Dict[str, Any]:
        """Enable an alert policy."""
        return self._post(f"alertPolicy/{policy_id}/enable")

    def get_alert_policy_automata(self, policy_id: str) -> Dict[str, Any]:
        """Get alert policy automata details."""
        return self._get(f"alertPolicy/automata/{policy_id}")

    def get_alert_notifications_by_entity(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """Get alert notifications by entity type and ID."""
        return self._get(f"alert/notifications/entity/{entity_type}/{entity_id}")

    def mark_alert_notifications_read(self, notification_ids: List[str]) -> Dict[str, Any]:
        """Mark alert notifications as read."""
        return self._post("alert/notifications/read", json_data={"notificationIds": notification_ids})

    # Notifiers Management
    def get_notifiers(self) -> Dict[str, Any]:
        """Get all notifiers."""
        return self._get("notifiers")

    def get_notifier(self, notifier_id: str) -> Dict[str, Any]:
        """Get specific notifier details."""
        return self._get(f"notifiers/{notifier_id}")

    def get_notifier_provider_configs(self) -> Dict[str, Any]:
        """Get notifier provider configurations."""
        return self._get("notifiers/providerConfigs")

    # End-to-End Latency Monitoring
    def get_topic_etelatency(self, topic_name: str, duration: Optional[str] = None, from_time: Optional[str] = None, to_time: Optional[str] = None) -> Dict[str, Any]:
        """Get end-to-end latency for a topic."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time:
            params["fromTime"] = from_time
        if to_time:
            params["toTime"] = to_time
        return self._get(f"etelatency/{topic_name}", params=params)

    def get_topic_group_etelatency(self, topic_name: str, group_name: str, duration: Optional[str] = None, from_time: Optional[str] = None, to_time: Optional[str] = None) -> Dict[str, Any]:
        """Get end-to-end latency for topic and consumer group."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time:
            params["fromTime"] = from_time
        if to_time:
            params["toTime"] = to_time
        return self._get(f"etelatency/{topic_name}/groups/{group_name}", params=params)

    # Replication Statistics
    def get_replication_stats(self) -> Dict[str, Any]:
        """Get replication statistics."""
        return self._get("replication-stats")

    def is_replication_configured(self) -> Dict[str, Any]:
        """Check if replication is configured."""
        return self._get("replication-stats/is-configured")

    def get_replication_stats_by_cluster(self, source: str, target: str) -> Dict[str, Any]:
        """Get replication stats by source and target clusters."""
        return self._get(f"replication-stats/topics/{source}/{target}")

    def get_topic_replication_stats(self, source: str, target: str, topic_name: str) -> Dict[str, Any]:
        """Get replication stats for specific topic."""
        return self._get(f"replication-stats/topics/{source}/{target}/{topic_name}")

    def get_topic_replication_stats_simple(self, topic_name: str) -> Dict[str, Any]:
        """Get simple replication stats for topic."""
        return self._get(f"replication-stats/topics/{topic_name}")

    # Kafka Connect Enhancements
    def get_connector_templates(self) -> Dict[str, Any]:
        """Get available connector templates."""
        return self._get("kafka-connect/connector-templates")

    def get_connector_config_definitions(self, connector_plugin_class: str) -> Dict[str, Any]:
        """Get connector configuration definitions."""
        return self._get(f"kafka-connect/connector-templates/config/definitions?connectorPluginClass={connector_plugin_class}")

    def get_connector_config_sample(self, name: str, connector_plugin_class: str, version: str) -> Dict[str, Any]:
        """Get sample connector configuration."""
        return self._get(f"kafka-connect/connector-templates/config/sample?name={name}&connectorPluginClass={connector_plugin_class}&version={version}")

    def validate_connector_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate connector configuration."""
        return self._post("kafka-connect/connector-templates/config/validate-detailed", json_data=config)

    def perform_connector_action(self, connector_name: str, action: str) -> Dict[str, Any]:
        """Perform connector actions (start, stop, restart, etc.)."""
        return self._post(f"kafka-connect/connectors/{connector_name}/{action}")

    def is_connect_configured(self) -> Dict[str, Any]:
        """Check if Kafka Connect is configured."""
        return self._get("kafka-connect/is-configured")

    def get_connector_sink_metrics(self, connector_name: str) -> Dict[str, Any]:
        """Get connector sink metrics."""
        return self._get(f"metrics/connect/sink/{connector_name}/0")

    def get_connect_worker_metrics(self, duration: Optional[str] = None, from_time: Optional[str] = None, to_time: Optional[str] = None) -> Dict[str, Any]:
        """Get Kafka Connect worker metrics."""
        params = {}
        if duration:
            params["duration"] = duration
        if from_time:
            params["fromTime"] = from_time
        if to_time:
            params["toTime"] = to_time
        return self._get("metrics/connect/workers", params=params)

    def get_access(self) -> Dict[str, Any]:
        """Get access information."""
        return self._get("authentication/access")
