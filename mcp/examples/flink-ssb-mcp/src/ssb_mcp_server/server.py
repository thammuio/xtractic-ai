from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import anyio

from .config import ServerConfig
from .auth import KnoxAuthFactory
from .client import SSBClient


# Lazy import of MCP to give a clear error if the dependency is missing
try:
	from mcp.server import FastMCP
	from mcp.server.stdio import stdio_server
except Exception as e:  # pragma: no cover
	raise RuntimeError(
		"The 'mcp' package is required. Install with: pip install mcp"
	) from e


def _redact_sensitive(obj: Any, max_items: int = 200) -> Any:
	"""Redact common sensitive fields and truncate large collections for LLMs."""
	redact_keys = {"password", "passcode", "token", "secret", "kerberosKeytab", "sslKeystorePasswd"}
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


def _handle_ssb_operation(operation_func, *args, **kwargs) -> Dict[str, Any]:
	"""Handle SSB operations with proper error handling and redaction."""
	try:
		data = operation_func(*args, **kwargs)
		return _redact_sensitive(data)
	except Exception as e:
		# Return error information in a structured format that Claude can understand
		error_response = {
			"error": True,
			"error_type": type(e).__name__,
			"error_message": str(e),
			"message": f"Operation failed: {str(e)}"
		}
		return error_response


def build_client(config: ServerConfig) -> SSBClient:
	verify = config.build_verify()
	ssb_base = config.build_ssb_base()
	
	# Use Knox authentication if Knox is configured, otherwise use direct SSB authentication
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
		# Direct SSB authentication
		import requests
		session = requests.Session()
		session.verify = verify
		if config.ssb_user and config.ssb_password:
			session.auth = (config.ssb_user, config.ssb_password)
	
	return SSBClient(
		ssb_base,
		session,
		timeout_seconds=config.timeout_seconds,
		proxy_context_path=config.proxy_context_path,
	)


def create_server(ssb: SSBClient, readonly: bool) -> FastMCP:
	app = FastMCP("ssb-mcp-server")

	@app.tool()
	async def get_ssb_info() -> Dict[str, Any]:
		"""Get SSB version and system information."""
		data = ssb.get_ssb_info()
		return _redact_sensitive(data)

	@app.tool()
	async def list_streams() -> Dict[str, Any]:
		"""List all SQL streams in SSB."""
		data = ssb.list_streams()
		return _redact_sensitive(data)

	@app.tool()
	async def get_stream(stream_name: str) -> Dict[str, Any]:
		"""Get details of a specific SQL stream."""
		data = ssb.get_stream(stream_name)
		return _redact_sensitive(data)

	@app.tool()
	async def get_stream_status(stream_name: str) -> Dict[str, Any]:
		"""Get the status of a SQL stream (running, stopped, etc.)."""
		data = ssb.get_stream_status(stream_name)
		return _redact_sensitive(data)

	@app.tool()
	async def get_stream_metrics(stream_name: str) -> Dict[str, Any]:
		"""Get performance metrics for a SQL stream."""
		data = ssb.get_stream_metrics(stream_name)
		return _redact_sensitive(data)

	@app.tool()
	async def list_tables() -> Dict[str, Any]:
		"""List all available tables in SSB."""
		data = ssb.list_tables()
		return _redact_sensitive(data)

	@app.tool()
	async def get_table_schema(table_name: str) -> Dict[str, Any]:
		"""Get schema information for a specific table."""
		data = ssb.get_table_schema(table_name)
		return _redact_sensitive(data)

	@app.tool()
	async def execute_query(sql_query: str, limit: Optional[int] = None) -> Dict[str, Any]:
		"""Execute a SQL query against SSB."""
		return _handle_ssb_operation(ssb.execute_query, sql_query, limit)

	@app.tool()
	async def list_udfs() -> Dict[str, Any]:
		"""List all available user-defined functions."""
		data = ssb.list_udfs()
		return _redact_sensitive(data)

	@app.tool()
	async def get_udf(udf_name: str) -> Dict[str, Any]:
		"""Get details of a specific user-defined function."""
		data = ssb.get_udf(udf_name)
		return _redact_sensitive(data)

	@app.tool()
	async def list_connectors() -> Dict[str, Any]:
		"""List all available connectors."""
		data = ssb.list_connectors()
		return _redact_sensitive(data)

	@app.tool()
	async def get_connector(connector_name: str) -> Dict[str, Any]:
		"""Get details of a specific connector."""
		data = ssb.get_connector(connector_name)
		return _redact_sensitive(data)

	@app.tool()
	async def list_topics() -> Dict[str, Any]:
		"""List all Kafka topics."""
		data = ssb.list_topics()
		return _redact_sensitive(data)

	@app.tool()
	async def get_topic(topic_name: str) -> Dict[str, Any]:
		"""Get details of a specific Kafka topic."""
		data = ssb.get_topic(topic_name)
		return _redact_sensitive(data)

	@app.tool()
	async def get_cluster_info() -> Dict[str, Any]:
		"""Get SSB cluster information."""
		data = ssb.get_cluster_info()
		return _redact_sensitive(data)

	@app.tool()
	async def get_cluster_health() -> Dict[str, Any]:
		"""Get SSB cluster health status."""
		data = ssb.get_cluster_health()
		return _redact_sensitive(data)
	
	@app.tool()
	async def get_job_status(job_id: int) -> Dict[str, Any]:
		"""Get status of a specific SSB job."""
		data = ssb.get_job_status(job_id)
		return _redact_sensitive(data)
	
	@app.tool()
	async def get_job_sample(sample_id: str) -> Dict[str, Any]:
		"""Get sample data from a job execution."""
		data = ssb.get_job_sample(sample_id)
		return _redact_sensitive(data)
	
	@app.tool()
	async def get_job_sample_by_id(job_id: int) -> Dict[str, Any]:
		"""Get sample data from a job by job ID."""
		data = ssb.get_job_sample_by_id(job_id)
		return _redact_sensitive(data)
	
	@app.tool()
	async def list_jobs_with_samples() -> Dict[str, Any]:
		"""List all jobs with their sample information."""
		data = ssb.list_jobs_with_samples()
		return _redact_sensitive(data)
	
	@app.tool()
	async def stop_job(job_id: int, savepoint: bool = True) -> Dict[str, Any]:
		"""Stop a specific SSB job."""
		data = ssb.stop_job(job_id, savepoint)
		return _redact_sensitive(data)
	
	@app.tool()
	async def execute_job(job_id: int, sql_query: str) -> Dict[str, Any]:
		"""Execute/restart a specific SSB job with new SQL."""
		data = ssb.execute_job(job_id, sql_query)
		return _redact_sensitive(data)
	
	@app.tool()
	async def configure_sampling(sample_id: str, sample_interval: int = 1000, sample_count: int = 100, window_size: int = 100, sample_all_messages: bool = False) -> Dict[str, Any]:
		"""Configure sampling parameters for a job."""
		data = ssb.configure_sampling(sample_id, sample_interval, sample_count, window_size, sample_all_messages)
		return _redact_sensitive(data)
	
	@app.tool()
	async def execute_query_with_sampling(sql_query: str, sample_interval: int = 1000, sample_count: int = 100, window_size: int = 100, sample_all_messages: bool = False) -> Dict[str, Any]:
		"""Execute a SQL query with proper sampling configuration."""
		data = ssb.execute_query_with_sampling(sql_query, sample_interval, sample_count, window_size, sample_all_messages)
		return _redact_sensitive(data)
	
	@app.tool()
	async def restart_job_with_sampling(job_id: int, sql_query: str, sample_interval: int = 1000, sample_all_messages: bool = False) -> Dict[str, Any]:
		"""Restart a job with new SQL and proper sampling configuration."""
		data = ssb.restart_job_with_sampling(job_id, sql_query, sample_interval, sample_all_messages)
		return _redact_sensitive(data)
	
	@app.tool()
	async def create_kafka_table(table_name: str, topic: str, kafka_connector_type: str = "local-kafka", 
	                           bootstrap_servers: str = "localhost:9092", format_type: str = "json",
	                           scan_startup_mode: str = "latest-offset", additional_properties: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
		"""Create a new table that only uses local-kafka connector."""
		return _handle_ssb_operation(ssb.create_kafka_table, table_name, topic, kafka_connector_type, bootstrap_servers, format_type, scan_startup_mode, additional_properties)
	
	@app.tool()
	async def validate_kafka_connector(kafka_connector_type: str) -> Dict[str, Any]:
		"""Validate that a connector type is the local-kafka connector and get its properties."""
		data = ssb.validate_kafka_connector(kafka_connector_type)
		return _redact_sensitive(data)
	
	@app.tool()
	async def register_kafka_table(table_name: str, topic: str, schema_fields: Optional[List[Dict[str, str]]] = None, use_ssb_prefix: bool = True, catalog: str = "ssb", database: str = "ssb_default") -> Dict[str, Any]:
		"""Register a Kafka table in the Flink catalog using DDL (makes it queryable)."""
		return _handle_ssb_operation(ssb.register_kafka_table, table_name, topic, schema_fields, use_ssb_prefix, catalog, database)

	# Write operations (only available if not in readonly mode)
	if not readonly:
		@app.tool()
		async def create_stream(stream_name: str, sql_query: str, description: Optional[str] = None) -> Dict[str, Any]:
			"""Create a new SQL stream."""
			data = ssb.create_stream(stream_name, sql_query, description)
			return _redact_sensitive(data)

		@app.tool()
		async def update_stream(stream_name: str, sql_query: str, description: Optional[str] = None) -> Dict[str, Any]:
			"""Update an existing SQL stream."""
			data = ssb.update_stream(stream_name, sql_query, description)
			return _redact_sensitive(data)

		@app.tool()
		async def delete_stream(stream_name: str) -> Dict[str, Any]:
			"""Delete a SQL stream."""
			data = ssb.delete_stream(stream_name)
			return _redact_sensitive(data)

		@app.tool()
		async def start_stream(stream_name: str) -> Dict[str, Any]:
			"""Start a SQL stream."""
			data = ssb.start_stream(stream_name)
			return _redact_sensitive(data)

		@app.tool()
		async def stop_stream(stream_name: str) -> Dict[str, Any]:
			"""Stop a SQL stream."""
			data = ssb.stop_stream(stream_name)
			return _redact_sensitive(data)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - ADVANCED JOB MANAGEMENT
	# ============================================================================
	
	@app.tool()
	async def get_job_events(job_id: int) -> Dict[str, Any]:
		"""Get detailed job event history and timeline."""
		return _handle_ssb_operation(ssb.get_job_events, job_id)
	
	@app.tool()
	async def get_job_state(job_id: int) -> Dict[str, Any]:
		"""Get comprehensive job state information."""
		return _handle_ssb_operation(ssb.get_job_state, job_id)
	
	@app.tool()
	async def get_job_mv_endpoints(job_id: int) -> Dict[str, Any]:
		"""Get materialized view endpoints for a job."""
		return _handle_ssb_operation(ssb.get_job_mv_endpoints, job_id)
	
	@app.tool()
	async def create_job_mv_endpoint(job_id: int, mv_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create or update a materialized view endpoint for a job."""
		return _handle_ssb_operation(ssb.create_job_mv_endpoint, job_id, mv_config)
	
	@app.tool()
	async def copy_job(job_id: int) -> Dict[str, Any]:
		"""Duplicate an existing job."""
		return _handle_ssb_operation(ssb.copy_job, job_id)
	
	@app.tool()
	async def copy_data_source(data_source_id: str) -> Dict[str, Any]:
		"""Clone a data source."""
		return _handle_ssb_operation(ssb.copy_data_source, data_source_id)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - MONITORING & DIAGNOSTICS
	# ============================================================================
	
	@app.tool()
	async def get_diagnostic_counters() -> Dict[str, Any]:
		"""Get system performance counters and diagnostics."""
		return _handle_ssb_operation(ssb.get_diagnostic_counters)
	
	@app.tool()
	async def get_heartbeat() -> Dict[str, Any]:
		"""Check system health and connectivity."""
		return _handle_ssb_operation(ssb.get_heartbeat)
	
	@app.tool()
	async def analyze_sql(sql_query: str) -> Dict[str, Any]:
		"""Analyze SQL query without execution (syntax, performance analysis)."""
		return _handle_ssb_operation(ssb.analyze_sql, sql_query)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - ENHANCED TABLE MANAGEMENT
	# ============================================================================
	
	@app.tool()
	async def list_tables_detailed() -> Dict[str, Any]:
		"""Get comprehensive table information."""
		return _handle_ssb_operation(ssb.list_tables_detailed)
	
	@app.tool()
	async def get_table_tree() -> Dict[str, Any]:
		"""Get hierarchical table structure organized by catalog."""
		return _handle_ssb_operation(ssb.get_table_tree)
	
	@app.tool()
	async def validate_data_source(data_source_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate data source configuration."""
		return _handle_ssb_operation(ssb.validate_data_source, data_source_config)
	
	@app.tool()
	async def create_table_detailed(table_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create table with full configuration."""
		return _handle_ssb_operation(ssb.create_table_detailed, table_config)
	
	@app.tool()
	async def get_table_details(table_id: str) -> Dict[str, Any]:
		"""Get detailed information about a specific table."""
		return _handle_ssb_operation(ssb.get_table_details, table_id)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - CONNECTOR & FORMAT MANAGEMENT
	# ============================================================================
	
	@app.tool()
	async def list_data_formats() -> Dict[str, Any]:
		"""List all available data formats."""
		return _handle_ssb_operation(ssb.list_data_formats)
	
	@app.tool()
	async def get_data_format_details(format_id: str) -> Dict[str, Any]:
		"""Get detailed information about a specific data format."""
		return _handle_ssb_operation(ssb.get_data_format_details, format_id)
	
	@app.tool()
	async def create_data_format(format_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create a new data format."""
		return _handle_ssb_operation(ssb.create_data_format, format_config)
	
	@app.tool()
	async def get_connector_jar(connector_type: str) -> Dict[str, Any]:
		"""Get connector JAR information."""
		return _handle_ssb_operation(ssb.get_connector_jar, connector_type)
	
	@app.tool()
	async def get_connector_type_details(connector_type: str) -> Dict[str, Any]:
		"""Get detailed connector type information."""
		return _handle_ssb_operation(ssb.get_connector_type_details, connector_type)
	
	@app.tool()
	async def get_connector_details(connector_id: str) -> Dict[str, Any]:
		"""Get detailed connector information."""
		return _handle_ssb_operation(ssb.get_connector_details, connector_id)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - USER & PROJECT MANAGEMENT
	# ============================================================================
	
	@app.tool()
	async def get_user_settings() -> Dict[str, Any]:
		"""Get user preferences and settings."""
		return _handle_ssb_operation(ssb.get_user_settings)
	
	@app.tool()
	async def update_user_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
		"""Update user configuration."""
		return _handle_ssb_operation(ssb.update_user_settings, settings)
	
	@app.tool()
	async def list_projects() -> Dict[str, Any]:
		"""List available projects."""
		return _handle_ssb_operation(ssb.list_projects)
	
	@app.tool()
	async def get_project_details(project_id: str) -> Dict[str, Any]:
		"""Get project information."""
		return _handle_ssb_operation(ssb.get_project_details, project_id)
	
	@app.tool()
	async def create_project(project_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create a new project."""
		return _handle_ssb_operation(ssb.create_project, project_config)
	
	@app.tool()
	async def get_user_info() -> Dict[str, Any]:
		"""Get current user information."""
		return _handle_ssb_operation(ssb.get_user_info)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - API KEY MANAGEMENT
	# ============================================================================
	
	@app.tool()
	async def list_api_keys() -> Dict[str, Any]:
		"""List user API keys."""
		return _handle_ssb_operation(ssb.list_api_keys)
	
	@app.tool()
	async def create_api_key(key_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create new API key."""
		return _handle_ssb_operation(ssb.create_api_key, key_config)
	
	@app.tool()
	async def delete_api_key(key_id: str) -> Dict[str, Any]:
		"""Delete API key."""
		return _handle_ssb_operation(ssb.delete_api_key, key_id)
	
	@app.tool()
	async def get_api_key_details(key_id: str) -> Dict[str, Any]:
		"""Get API key information."""
		return _handle_ssb_operation(ssb.get_api_key_details, key_id)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - ENVIRONMENT MANAGEMENT
	# ============================================================================
	
	@app.tool()
	async def list_environments() -> Dict[str, Any]:
		"""List available environments."""
		return _handle_ssb_operation(ssb.list_environments)
	
	@app.tool()
	async def activate_environment(env_id: str) -> Dict[str, Any]:
		"""Activate/switch to an environment."""
		return _handle_ssb_operation(ssb.activate_environment, env_id)
	
	@app.tool()
	async def get_environment_details(env_id: str) -> Dict[str, Any]:
		"""Get environment configuration."""
		return _handle_ssb_operation(ssb.get_environment_details, env_id)
	
	@app.tool()
	async def create_environment(env_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create new environment."""
		return _handle_ssb_operation(ssb.create_environment, env_config)
	
	@app.tool()
	async def deactivate_environment() -> Dict[str, Any]:
		"""Deactivate current environment."""
		return _handle_ssb_operation(ssb.deactivate_environment)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - SYNC & CONFIGURATION
	# ============================================================================
	
	@app.tool()
	async def get_sync_config() -> Dict[str, Any]:
		"""Get sync configuration."""
		return _handle_ssb_operation(ssb.get_sync_config)
	
	@app.tool()
	async def update_sync_config(config: Dict[str, Any]) -> Dict[str, Any]:
		"""Update sync configuration."""
		return _handle_ssb_operation(ssb.update_sync_config, config)
	
	@app.tool()
	async def delete_sync_config() -> Dict[str, Any]:
		"""Delete sync configuration."""
		return _handle_ssb_operation(ssb.delete_sync_config)
	
	@app.tool()
	async def validate_sync_config(project: str) -> Dict[str, Any]:
		"""Validate sync configuration for a project."""
		return _handle_ssb_operation(ssb.validate_sync_config, project)
	
	@app.tool()
	async def export_project(project: str) -> Dict[str, Any]:
		"""Export project configuration."""
		return _handle_ssb_operation(ssb.export_project, project)
	
	@app.tool()
	async def import_project(project: str, config: Dict[str, Any]) -> Dict[str, Any]:
		"""Import project configuration."""
		return _handle_ssb_operation(ssb.import_project, project, config)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - UDF MANAGEMENT
	# ============================================================================
	
	@app.tool()
	async def list_udfs_detailed() -> Dict[str, Any]:
		"""Get comprehensive UDF information."""
		return _handle_ssb_operation(ssb.list_udfs_detailed)
	
	@app.tool()
	async def run_udf(udf_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
		"""Execute UDF function."""
		return _handle_ssb_operation(ssb.run_udf, udf_id, parameters)
	
	@app.tool()
	async def get_udf_artifacts() -> Dict[str, Any]:
		"""Get UDF artifacts and dependencies."""
		return _handle_ssb_operation(ssb.get_udf_artifacts)
	
	@app.tool()
	async def create_udf(udf_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create custom UDF."""
		return _handle_ssb_operation(ssb.create_udf, udf_config)
	
	@app.tool()
	async def update_udf(udf_id: str, udf_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Update UDF configuration."""
		return _handle_ssb_operation(ssb.update_udf, udf_id, udf_config)
	
	@app.tool()
	async def get_udf_details(udf_id: str) -> Dict[str, Any]:
		"""Get detailed UDF information."""
		return _handle_ssb_operation(ssb.get_udf_details, udf_id)
	
	@app.tool()
	async def get_udf_artifact_details(artifact_id: str) -> Dict[str, Any]:
		"""Get UDF artifact details."""
		return _handle_ssb_operation(ssb.get_udf_artifact_details, artifact_id)
	
	@app.tool()
	async def get_udf_artifact_by_type(artifact_type: str) -> Dict[str, Any]:
		"""Get UDF artifacts by type."""
		return _handle_ssb_operation(ssb.get_udf_artifact_by_type, artifact_type)

	return app


async def run_stdio() -> None:
	# For FastMCP, prefer the built-in stdio runner
	config = ServerConfig()
	ssb = build_client(config)
	server = create_server(ssb, readonly=config.readonly)
	# run() is synchronous; call the async flavor directly
	await server.run_stdio_async()


def main() -> None:
	transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
	if transport != "stdio":
		# Defer to FastMCP synchronous run helper for other transports when added
		config = ServerConfig()
		ssb = build_client(config)
		server = create_server(ssb, readonly=config.readonly)
		server.run(transport=transport)
		return
	anyio.run(run_stdio)


if __name__ == "__main__":
	main()
