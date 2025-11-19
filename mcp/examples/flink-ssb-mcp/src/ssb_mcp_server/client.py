from __future__ import annotations

import time
from typing import Any, Dict, Optional, List
from functools import lru_cache

import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


class SSBError(Exception):
	pass


class SSBClient:
	def __init__(self, base_url: str, session: requests.Session, timeout_seconds: int = 30, proxy_context_path: Optional[str] = None):
		self.base_url = base_url.rstrip("/")
		self.session = session
		self.timeout = timeout_seconds
		self.proxy_context_path = proxy_context_path
		
		# Add CDP proxy headers if configured
		if self.proxy_context_path:
			self.session.headers.update({'X-ProxyContextPath': self.proxy_context_path})

	def _url(self, path: str) -> str:
		return f"{self.base_url}/{path.lstrip('/')}"

	@retry(
		retry=retry_if_exception_type((requests.HTTPError, requests.ConnectionError, requests.Timeout)),
		wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
		stop=stop_after_attempt(3),
		reraise=True,
	)
	def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
		resp = self.session.get(self._url(path), params=params, timeout=self.timeout)
		if resp.status_code == 401:
			raise requests.HTTPError("Unauthorized", response=resp)
		if resp.status_code == 403:
			raise requests.HTTPError("Forbidden", response=resp)
		if not resp.ok:
			# Try to get detailed error message from response
			try:
				error_data = resp.json()
				error_message = error_data.get('error_message', f'HTTP {resp.status_code} Error')
			except:
				error_message = f'HTTP {resp.status_code} Error: {resp.text}'
			raise SSBError(f"{error_message} for {path}")
		return resp.json()

	@retry(
		retry=retry_if_exception_type((requests.HTTPError, requests.ConnectionError, requests.Timeout)),
		wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
		stop=stop_after_attempt(3),
		reraise=True,
	)
	def _post(self, path: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
		resp = self.session.post(self._url(path), data=data, json=json_data, timeout=self.timeout)
		if resp.status_code == 401:
			raise requests.HTTPError("Unauthorized", response=resp)
		if resp.status_code == 403:
			raise requests.HTTPError("Forbidden", response=resp)
		if not resp.ok:
			# Try to get detailed error message from response
			try:
				error_data = resp.json()
				error_message = error_data.get('error_message', f'HTTP {resp.status_code} Error')
			except:
				error_message = f'HTTP {resp.status_code} Error: {resp.text}'
			raise SSBError(f"{error_message} for {path}")
		return resp.json()

	@retry(
		retry=retry_if_exception_type((requests.HTTPError, requests.ConnectionError, requests.Timeout)),
		wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
		stop=stop_after_attempt(3),
		reraise=True,
	)
	def _put(self, path: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
		resp = self.session.put(self._url(path), data=data, json=json_data, timeout=self.timeout)
		if resp.status_code == 401:
			raise requests.HTTPError("Unauthorized", response=resp)
		if resp.status_code == 403:
			raise requests.HTTPError("Forbidden", response=resp)
		resp.raise_for_status()
		return resp.json()

	@retry(
		retry=retry_if_exception_type((requests.HTTPError, requests.ConnectionError, requests.Timeout)),
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

	# SSB API Methods
	
	def get_ssb_info(self) -> Dict[str, Any]:
		"""Get SSB version and system information."""
		# Use jobs endpoint to get SSB information
		jobs = self._get("api/v1/jobs")
		return {
			"status": "connected",
			"jobs_count": len(jobs.get("jobs", [])),
			"message": "SSB MCP Server connected successfully"
		}

	def list_streams(self) -> Dict[str, Any]:
		"""List all SQL streams (jobs)."""
		return self._get("api/v1/jobs")

	def get_stream(self, stream_name: str) -> Dict[str, Any]:
		"""Get details of a specific stream (job)."""
		# For now, return job list and filter by name
		jobs = self._get("api/v1/jobs")
		for job in jobs.get("jobs", []):
			if job.get("name") == stream_name:
				return job
		raise SSBError(f"Stream '{stream_name}' not found")

	def create_stream(self, stream_name: str, sql_query: str, description: Optional[str] = None) -> Dict[str, Any]:
		"""Create a new SQL stream (job)."""
		data = {
			"sql": sql_query,
			"job_config": {
				"job_name": stream_name
			}
		}
		return self._post("api/v1/jobs", json_data=data)

	def update_stream(self, stream_name: str, sql_query: str, description: Optional[str] = None) -> Dict[str, Any]:
		"""Update an existing SQL stream."""
		data = {
			"name": stream_name,
			"sql": sql_query,
			"description": description or ""
		}
		return self._put(f"streams/{stream_name}", json_data=data)

	def delete_stream(self, stream_name: str) -> Dict[str, Any]:
		"""Delete a SQL stream."""
		return self._delete(f"streams/{stream_name}")

	def start_stream(self, stream_name: str) -> Dict[str, Any]:
		"""Start a SQL stream."""
		return self._post(f"streams/{stream_name}/start")

	def stop_stream(self, stream_name: str) -> Dict[str, Any]:
		"""Stop a SQL stream."""
		return self._post(f"streams/{stream_name}/stop")

	def get_stream_status(self, stream_name: str) -> Dict[str, Any]:
		"""Get the status of a SQL stream."""
		return self._get(f"streams/{stream_name}/status")

	def get_stream_metrics(self, stream_name: str) -> Dict[str, Any]:
		"""Get metrics for a SQL stream."""
		return self._get(f"streams/{stream_name}/metrics")

	def list_tables(self) -> Dict[str, Any]:
		"""List all available tables."""
		# Use data sources endpoint as tables in SSB
		return self._get("api/v1/data-sources")

	def get_table_schema(self, table_name: str) -> Dict[str, Any]:
		"""Get schema for a specific table."""
		# For now, return a placeholder since SSB doesn't have direct schema endpoint
		return {"message": f"Schema for table '{table_name}' not available via API", "table_name": table_name}

	def execute_query(self, sql_query: str, limit: Optional[int] = None, sample_interval: int = 1000, sample_count: int = 100, window_size: int = 100, sample_all_messages: bool = False) -> Dict[str, Any]:
		"""Execute a SQL query."""
		# Ensure SQL statement ends with semicolon
		sql_query = sql_query.strip()
		if not sql_query.endswith(';'):
			sql_query += ';'
		
		data = {"sql": sql_query}
		
		# Add job configuration for sampling
		if sample_all_messages:
			# For sample all messages, use very frequent sampling
			data["job_config"] = {
				"job_name": f"job_by_admin_at_{int(time.time() * 1000)}",
				"runtime_config": {
					"execution_mode": "SESSION",
					"parallelism": 1,
					"sample_interval": 0,  # Sample immediately
					"sample_count": 10000,  # High count
					"window_size": 10000,   # Large window
					"start_with_savepoint": False
				}
			}
		elif sample_interval != 1000 or sample_count != 100 or window_size != 100:
			# Custom sampling configuration
			data["job_config"] = {
				"job_name": f"job_by_admin_at_{int(time.time() * 1000)}",
				"runtime_config": {
					"execution_mode": "SESSION",
					"parallelism": 1,
					"sample_interval": sample_interval,
					"sample_count": sample_count,
					"window_size": window_size,
					"start_with_savepoint": False
				}
			}
		
		response = self._post("api/v1/sql/execute", json_data=data)
		
		# Enhance the response with more context
		if response.get("type") == "job":
			response["message"] = f"SQL query executed successfully! A new SSB job has been created."
			response["job_url"] = f"http://localhost:8081/#/job/{response.get('flink_job_id', 'unknown')}"
			response["status"] = "success"
			if sample_all_messages:
				response["sampling_mode"] = "sample_all_messages"
				response["sample_interval"] = 0
				response["sample_count"] = 10000
				response["window_size"] = 10000
		else:
			response["status"] = "completed"
			
		return response
	
	def execute_query_with_sampling(self, sql_query: str, sample_interval: int = 1000, sample_count: int = 100, window_size: int = 100, sample_all_messages: bool = False) -> Dict[str, Any]:
		"""Execute a SQL query with proper sampling configuration."""
		# Execute the query with sampling configuration
		response = self.execute_query(sql_query, sample_interval=sample_interval, sample_count=sample_count, window_size=window_size, sample_all_messages=sample_all_messages)
		
		# Add sampling information to response
		if response.get("type") == "job":
			response["sampling_configured"] = True
			response["sample_interval"] = 0 if sample_all_messages else sample_interval
			response["sample_count"] = 10000 if sample_all_messages else sample_count
			response["window_size"] = 10000 if sample_all_messages else window_size
			response["sample_all_messages"] = sample_all_messages
		
		return response
	
	def restart_job_with_sampling(self, job_id: int, sql_query: str, sample_interval: int = 1000, sample_all_messages: bool = False) -> Dict[str, Any]:
		"""Restart a job with new SQL and proper sampling configuration."""
		# Ensure SQL statement ends with semicolon
		sql_query = sql_query.strip()
		if not sql_query.endswith(';'):
			sql_query += ';'
		
		# First try to stop the job
		try:
			stop_result = self.stop_job(job_id, savepoint=True)
		except Exception as e:
			# If stop fails, continue anyway
			pass
		
		# Create a new job with the same SQL
		response = self.execute_query_with_sampling(sql_query, sample_interval, sample_all_messages=sample_all_messages)
		
		# Add information about the restart
		response["restarted_from_job_id"] = job_id
		response["message"] = f"Job {job_id} restarted with new configuration"
		if sample_all_messages:
			response["message"] += " (sampling all messages)"
		
		return response

	def list_udfs(self) -> Dict[str, Any]:
		"""List all available user-defined functions."""
		# SSB doesn't have a direct UDFs endpoint, return empty list
		return {"udfs": []}

	def get_udf(self, udf_name: str) -> Dict[str, Any]:
		"""Get details of a specific UDF."""
		return {"message": f"UDF '{udf_name}' not found", "udf_name": udf_name}

	def list_connectors(self) -> Dict[str, Any]:
		"""List all available connectors."""
		return self._get("api/v1/ddl/connectors")

	def get_connector(self, connector_name: str) -> Dict[str, Any]:
		"""Get details of a specific connector."""
		# For now, return a placeholder since we need to filter from the list
		connectors = self._get("api/v1/ddl/connectors")
		for connector in connectors:
			if connector.get("type") == connector_name:
				return connector
		return {"message": f"Connector '{connector_name}' not found", "connector_name": connector_name}

	def list_topics(self) -> Dict[str, Any]:
		"""List all Kafka topics."""
		# SSB doesn't directly manage Kafka topics, return empty list
		return {"topics": [], "message": "Kafka topics are managed by the Kafka service, not SSB"}

	def get_topic(self, topic_name: str) -> Dict[str, Any]:
		"""Get details of a specific Kafka topic."""
		return {"message": f"Topic '{topic_name}' details not available via SSB API", "topic_name": topic_name}

	def get_cluster_info(self) -> Dict[str, Any]:
		"""Get cluster information."""
		return self._get("cluster/info")
	
	def get_job_status(self, job_id: int) -> Dict[str, Any]:
		"""Get status of a specific job."""
		jobs = self._get("api/v1/jobs")
		for job in jobs.get("jobs", []):
			if job.get("job_id") == job_id:
				return job
		return {"message": f"Job {job_id} not found", "job_id": job_id}
	
	def get_job_sample(self, sample_id: str) -> Dict[str, Any]:
		"""Get sample data from a job execution."""
		try:
			response = self._get(f"api/v1/samples/{sample_id}")
			# Add helpful context to the response
			if response.get("records"):
				response["message"] = f"Retrieved {len(response['records'])} sample records"
			else:
				response["message"] = "No sample data available yet. The job may still be processing or hasn't produced data."
			return response
		except Exception as e:
			return {
				"error": str(e),
				"message": f"Failed to retrieve sample data for {sample_id}",
				"sample_id": sample_id
			}
	
	def get_job_sample_by_id(self, job_id: int) -> Dict[str, Any]:
		"""Get sample data from a job by job ID."""
		job = self.get_job_status(job_id)
		if "sample_id" in job:
			return self.get_job_sample(job["sample_id"])
		else:
			return {"message": f"No sample data available for job {job_id}", "job_id": job_id}

	def get_cluster_health(self) -> Dict[str, Any]:
		"""Get cluster health status."""
		return self._get("cluster/health")
	
	def stop_job(self, job_id: int, savepoint: bool = True) -> Dict[str, Any]:
		"""Stop a specific SSB job."""
		data = {"savepoint": savepoint}
		return self._post(f"api/v1/jobs/{job_id}/stop", json_data=data)
	
	def execute_job(self, job_id: int, sql_query: str) -> Dict[str, Any]:
		"""Execute/restart a specific SSB job with new SQL."""
		# Ensure SQL statement ends with semicolon
		sql_query = sql_query.strip()
		if not sql_query.endswith(';'):
			sql_query += ';'
		
		data = {"sql": sql_query}
		return self._post(f"api/v1/jobs/{job_id}/execute", json_data=data)
	
	def configure_sampling(self, sample_id: str, sample_interval: int = 1000, sample_count: int = 100, window_size: int = 100, sample_all_messages: bool = False) -> Dict[str, Any]:
		"""Configure sampling parameters for a job."""
		data = {
			"position": "latest",  # Start from latest data
			"sample_interval": sample_interval,
			"sample_count": sample_count,
			"window_size": window_size
		}
		
		# If sampling all messages, set interval to 0 and high count
		if sample_all_messages:
			data["sample_interval"] = 0
			data["sample_count"] = 10000  # High count to capture all messages
			data["window_size"] = 10000
		
		return self._post(f"api/v1/samples/{sample_id}/configure", json_data=data)
	
	def list_jobs_with_samples(self) -> Dict[str, Any]:
		"""List all jobs with their sample information."""
		jobs = self._get("api/v1/jobs")
		job_list = []
		for job in jobs.get("jobs", []):
			job_info = {
				"job_id": job.get("job_id"),
				"name": job.get("name"),
				"state": job.get("state"),
				"sample_id": job.get("sample_id"),
				"created_at": job.get("created_at"),
				"flink_job_id": job.get("flink_job_id")
			}
			# Try to get sample data for each job
			if job.get("sample_id"):
				try:
					sample_data = self.get_job_sample(job["sample_id"])
					job_info["sample_records_count"] = len(sample_data.get("records", []))
					job_info["sample_status"] = sample_data.get("job_status", "unknown")
				except:
					job_info["sample_records_count"] = 0
					job_info["sample_status"] = "error"
			else:
				job_info["sample_records_count"] = 0
				job_info["sample_status"] = "no_sample_id"
			job_list.append(job_info)
		
		return {
			"jobs": job_list,
			"total_jobs": len(job_list),
			"running_jobs": len([j for j in job_list if j["state"] == "RUNNING"]),
			"message": f"Found {len(job_list)} jobs with sample information"
		}
	
	def create_kafka_table(self, table_name: str, topic: str, kafka_connector_type: str = "local-kafka", 
	                      bootstrap_servers: str = "localhost:9092", format_type: str = "json",
	                      scan_startup_mode: str = "latest-offset", additional_properties: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
		"""Create a new table that only uses local-kafka connector."""
		
		# Enforce that only local-kafka connector is used
		if kafka_connector_type != "local-kafka":
			raise SSBError(f"Only 'local-kafka' connector is allowed for virtual tables. Provided: '{kafka_connector_type}'")
		
		# Build properties for the data source
		properties = {
			"connector": kafka_connector_type,
			"topic": topic,
			"properties.bootstrap.servers": bootstrap_servers,
			"scan.startup.mode": scan_startup_mode
		}
		
		# Add format configuration
		if format_type.lower() == "json":
			properties["format"] = "json"
		elif format_type.lower() == "csv":
			properties["format"] = "csv"
		elif format_type.lower() == "avro":
			properties["format"] = "avro"
		else:
			properties["format"] = format_type
		
		# Add any additional properties
		if additional_properties:
			properties.update(additional_properties)
		
		# Create the data source
		data_source = {
			"name": table_name,
			"type": kafka_connector_type,
			"properties": properties
		}
		
		try:
			response = self._post("api/v1/data-sources", json_data=data_source)
			response["message"] = f"Kafka table '{table_name}' created successfully with connector '{kafka_connector_type}'"
			response["kafka_topic"] = topic
			response["bootstrap_servers"] = bootstrap_servers
			response["format"] = format_type
			response["connector_type"] = kafka_connector_type
			return response
		except Exception as e:
			raise SSBError(f"Failed to create Kafka table '{table_name}': {str(e)}")
	
	def validate_kafka_connector(self, kafka_connector_type: str) -> Dict[str, Any]:
		"""Validate that a connector type is the local-kafka connector."""
		allowed_connector = "local-kafka"
		
		if kafka_connector_type != allowed_connector:
			return {
				"valid": False,
				"message": f"Only '{allowed_connector}' connector is allowed for virtual tables. Provided: '{kafka_connector_type}'",
				"allowed_connector": allowed_connector
			}
		
		# Get connector details
		try:
			connectors = self._get("api/v1/ddl/connectors")
			kafka_connector = None
			for connector in connectors:
				if connector.get("type") == kafka_connector_type:
					kafka_connector = connector
					break
			
			if kafka_connector:
				return {
					"valid": True,
					"message": f"Connector '{kafka_connector_type}' is a valid Kafka connector",
					"connector_type": kafka_connector_type,
					"properties": kafka_connector.get("properties", []),
					"supported_formats": kafka_connector.get("supported_formats", [])
				}
			else:
				return {
					"valid": False,
					"message": f"Kafka connector '{kafka_connector_type}' not found in available connectors"
				}
		except Exception as e:
			return {
				"valid": False,
				"message": f"Error validating connector: {str(e)}"
			}
	
	def register_kafka_table(self, table_name: str, topic: str, schema_fields: Optional[List[Dict[str, str]]] = None, use_ssb_prefix: bool = True, catalog: str = "ssb", database: str = "ssb_default") -> Dict[str, Any]:
		"""Register a Kafka table in the Flink catalog using DDL with the specified template."""
		
		# Check if the requested catalog exists, fallback to default_catalog if not
		try:
			catalogs_result = self._post("api/v1/sql/execute", json_data={"sql": "SHOW CATALOGS;"})
			available_catalogs = []
			if catalogs_result.get("table_data"):
				available_catalogs = [cat.get("catalog name", "") for cat in catalogs_result["table_data"]["data"]]
			
			if catalog not in available_catalogs:
				original_catalog = catalog
				catalog = "default_catalog"
				print(f"Warning: Catalog '{original_catalog}' not available, using '{catalog}' instead")
		except:
			# If we can't check catalogs, use default_catalog as fallback
			if catalog == "ssb":
				catalog = "default_catalog"
		
		# Add ssb_ prefix if requested and not already present
		if use_ssb_prefix and not table_name.startswith('ssb_'):
			full_table_name = f"ssb_{table_name}"
		else:
			full_table_name = table_name
		
		# Default schema for NVDA-like data if not provided
		if schema_fields is None:
			schema_fields = [
				{"name": "___open", "type": "VARCHAR(2147483647)"},
				{"name": "___high", "type": "VARCHAR(2147483647)"},
				{"name": "___low", "type": "VARCHAR(2147483647)"},
				{"name": "___close", "type": "VARCHAR(2147483647)"},
				{"name": "___volume", "type": "VARCHAR(2147483647)"},
				{"name": "eventTimestamp", "type": "TIMESTAMP(3) WITH LOCAL TIME ZONE METADATA FROM 'timestamp'"}
			]
		
		# Build the DDL statement using the specified template
		columns = []
		for field in schema_fields:
			field_name = field.get("name", "unknown")
			field_type = field.get("type", "VARCHAR(2147483647)")
			columns.append(f"  `{field_name}` {field_type}")
		
		# Add watermark for eventTimestamp if it exists
		watermark_clause = ""
		has_event_timestamp = any(field.get("name") == "eventTimestamp" for field in schema_fields)
		if has_event_timestamp:
			watermark_clause = ",\n  WATERMARK FOR `eventTimestamp` AS `eventTimestamp` - INTERVAL '3' SECOND"
		
		# Join columns outside f-string to avoid backslash in f-string expression
		columns_str = ',\n'.join(columns)
		
		ddl_sql = f"""CREATE TABLE `{catalog}`.`{database}`.`{full_table_name}` (
{columns_str}{watermark_clause}
) WITH (
  'scan.startup.mode' = 'earliest-offset',
  'properties.request.timeout.ms' = '120000',
  'properties.auto.offset.reset' = 'earliest',
  'format' = 'json',
  'properties.bootstrap.servers' = 'kafka:9092',
  'connector' = 'kafka',
  'properties.transaction.timeout.ms' = '900000',
  'topic' = '{topic}'
);"""
		
		try:
			# Execute the DDL
			response = self._post("api/v1/sql/execute", json_data={"sql": ddl_sql})
			
			# Check if table is now available by switching to the target database
			try:
				# Switch to target database
				self._post("api/v1/sql/execute", json_data={"sql": f"USE {catalog}.{database};"})
				# Check tables in target database
				available_tables = self._post("api/v1/sql/execute", json_data={"sql": "SHOW TABLES;"})
				table_available = False
				if available_tables.get("table_data"):
					for table in available_tables["table_data"]["data"]:
						if table.get("table name") == full_table_name:
							table_available = True
							break
				# Switch back to default_database
				self._post("api/v1/sql/execute", json_data={"sql": "USE default_catalog.default_database;"})
			except:
				table_available = False
			
			response["message"] = f"Table '{full_table_name}' registered in Flink catalog successfully using template"
			response["table_name"] = full_table_name
			response["original_name"] = table_name
			response["topic"] = topic
			response["connector"] = "kafka"
			response["catalog"] = catalog
			response["database"] = database
			response["full_namespace"] = f"{catalog}.{database}"
			response["available_for_querying"] = table_available
			response["ddl_used"] = ddl_sql
			response["ssb_prefix_applied"] = use_ssb_prefix and not table_name.startswith('ssb_')
			response["template_used"] = "ssb.ssb_default template with watermark and kafka connector"
			
			return response
		except Exception as e:
			raise SSBError(f"Failed to register table '{full_table_name}' in Flink catalog: {str(e)}")

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - ADVANCED JOB MANAGEMENT
	# ============================================================================
	
	def get_job_events(self, job_id: int) -> Dict[str, Any]:
		"""Get detailed job event history and timeline."""
		return self._get(f"api/v1/jobs/{job_id}/events")
	
	def get_job_state(self, job_id: int) -> Dict[str, Any]:
		"""Get comprehensive job state information."""
		return self._get(f"api/v1/jobs/{job_id}/state")
	
	def get_job_mv_endpoints(self, job_id: int) -> Dict[str, Any]:
		"""Get materialized view endpoints for a job."""
		return self._get(f"api/v1/jobs/{job_id}/mv")
	
	def create_job_mv_endpoint(self, job_id: int, mv_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create or update a materialized view endpoint for a job."""
		return self._post(f"api/v1/jobs/{job_id}/mv", json_data=mv_config)
	
	def copy_job(self, job_id: int) -> Dict[str, Any]:
		"""Duplicate an existing job."""
		return self._post(f"api/v1/jobs/{job_id}/copy")
	
	def copy_data_source(self, data_source_id: str) -> Dict[str, Any]:
		"""Clone a data source."""
		return self._post(f"api/v1/data-sources/{data_source_id}/copy")

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - MONITORING & DIAGNOSTICS
	# ============================================================================
	
	def get_diagnostic_counters(self) -> Dict[str, Any]:
		"""Get system performance counters and diagnostics."""
		return self._get("api/v1/diag/counters")
	
	def get_heartbeat(self) -> Dict[str, Any]:
		"""Check system health and connectivity."""
		return self._get("api/v1/heartbeat")
	
	def analyze_sql(self, sql_query: str) -> Dict[str, Any]:
		"""Analyze SQL query without execution (syntax, performance analysis)."""
		return self._post("api/v1/sql/analyze", json_data={"sql": sql_query})

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - ENHANCED TABLE MANAGEMENT
	# ============================================================================
	
	def list_tables_detailed(self) -> Dict[str, Any]:
		"""Get comprehensive table information."""
		result = self._get("api/v1/tables")
		# Handle both list and dict responses
		if isinstance(result, list):
			return {"tables": result}
		return result
	
	def get_table_tree(self) -> Dict[str, Any]:
		"""Get hierarchical table structure organized by catalog."""
		return self._get("api/v1/tables/tree")
	
	def validate_data_source(self, data_source_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate data source configuration."""
		return self._post("api/v1/data-sources/validate", json_data=data_source_config)
	
	def create_table_detailed(self, table_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create table with full configuration."""
		return self._post("api/v1/tables", json_data=table_config)
	
	def get_table_details(self, table_id: str) -> Dict[str, Any]:
		"""Get detailed information about a specific table."""
		return self._get(f"api/v1/tables/{table_id}")

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - CONNECTOR & FORMAT MANAGEMENT
	# ============================================================================
	
	def list_data_formats(self) -> Dict[str, Any]:
		"""List all available data formats."""
		result = self._get("api/v1/ddl/data-formats")
		# Handle both list and dict responses
		if isinstance(result, list):
			return {"dataFormats": result}
		return result
	
	def get_data_format_details(self, format_id: str) -> Dict[str, Any]:
		"""Get detailed information about a specific data format."""
		return self._get(f"api/v1/ddl/data-formats/{format_id}")
	
	def create_data_format(self, format_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create a new data format."""
		return self._post("api/v1/ddl/data-formats", json_data=format_config)
	
	def get_connector_jar(self, connector_type: str) -> Dict[str, Any]:
		"""Get connector JAR information."""
		return self._get(f"api/v1/ddl/connectors/jar/{connector_type}")
	
	def get_connector_type_details(self, connector_type: str) -> Dict[str, Any]:
		"""Get detailed connector type information."""
		return self._get(f"api/v1/ddl/connectors/type/{connector_type}")
	
	def get_connector_details(self, connector_id: str) -> Dict[str, Any]:
		"""Get detailed connector information."""
		return self._get(f"api/v1/ddl/connectors/{connector_id}")

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - USER & PROJECT MANAGEMENT
	# ============================================================================
	
	def get_user_settings(self) -> Dict[str, Any]:
		"""Get user preferences and settings."""
		return self._get("api/v1/user/settings")
	
	def update_user_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
		"""Update user configuration."""
		return self._put("api/v1/user/settings", json_data=settings)
	
	def list_projects(self) -> Dict[str, Any]:
		"""List available projects."""
		result = self._get("api/v1/projects")
		# Handle both list and dict responses
		if isinstance(result, list):
			return {"projects": result}
		return result
	
	def get_project_details(self, project_id: str) -> Dict[str, Any]:
		"""Get project information."""
		return self._get(f"api/v1/projects/{project_id}")
	
	def create_project(self, project_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create a new project."""
		return self._post("api/v1/projects", json_data=project_config)
	
	def get_user_info(self) -> Dict[str, Any]:
		"""Get current user information."""
		return self._get("api/v1/user")

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - API KEY MANAGEMENT
	# ============================================================================
	
	def list_api_keys(self) -> Dict[str, Any]:
		"""List user API keys."""
		return self._get("api/v1/api-keys")
	
	def create_api_key(self, key_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create new API key."""
		return self._post("api/v1/api-keys", json_data=key_config)
	
	def delete_api_key(self, key_id: str) -> Dict[str, Any]:
		"""Delete API key."""
		return self._delete(f"api/v1/api-keys/{key_id}")
	
	def get_api_key_details(self, key_id: str) -> Dict[str, Any]:
		"""Get API key information."""
		return self._get(f"api/v1/api-keys/{key_id}")

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - ENVIRONMENT MANAGEMENT
	# ============================================================================
	
	def list_environments(self) -> Dict[str, Any]:
		"""List available environments."""
		result = self._get("api/v1/environments")
		# Handle both list and dict responses
		if isinstance(result, list):
			return {"environments": result}
		return result
	
	def activate_environment(self, env_id: str) -> Dict[str, Any]:
		"""Activate/switch to an environment."""
		return self._post(f"api/v1/environments/{env_id}/activate")
	
	def get_environment_details(self, env_id: str) -> Dict[str, Any]:
		"""Get environment configuration."""
		return self._get(f"api/v1/environments/{env_id}")
	
	def create_environment(self, env_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create new environment."""
		return self._post("api/v1/environments", json_data=env_config)
	
	def deactivate_environment(self) -> Dict[str, Any]:
		"""Deactivate current environment."""
		return self._post("api/v1/environments/deactivate")

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - SYNC & CONFIGURATION
	# ============================================================================
	
	def get_sync_config(self) -> Dict[str, Any]:
		"""Get sync configuration."""
		return self._get("api/v1/sync/config")
	
	def update_sync_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
		"""Update sync configuration."""
		return self._post("api/v1/sync/config", json_data=config)
	
	def delete_sync_config(self) -> Dict[str, Any]:
		"""Delete sync configuration."""
		return self._delete("api/v1/sync/config")
	
	def validate_sync_config(self, project: str) -> Dict[str, Any]:
		"""Validate sync configuration for a project."""
		return self._post(f"api/v1/sync/config/validate/{project}")
	
	def export_project(self, project: str) -> Dict[str, Any]:
		"""Export project configuration."""
		return self._get(f"api/v1/sync/git/export/{project}")
	
	def import_project(self, project: str, config: Dict[str, Any]) -> Dict[str, Any]:
		"""Import project configuration."""
		return self._post(f"api/v1/sync/git/import/{project}", json_data=config)

	# ============================================================================
	# HIGH-PRIORITY ADDITIONS - UDF MANAGEMENT
	# ============================================================================
	
	def list_udfs_detailed(self) -> Dict[str, Any]:
		"""Get comprehensive UDF information."""
		result = self._get("api/v1/udfs")
		# Handle both list and dict responses
		if isinstance(result, list):
			return {"udfs": result}
		return result
	
	def run_udf(self, udf_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
		"""Execute UDF function."""
		return self._post("api/v1/udfs/run", json_data={"udfId": udf_id, "parameters": parameters})
	
	def get_udf_artifacts(self) -> Dict[str, Any]:
		"""Get UDF artifacts and dependencies."""
		return self._get("api/v1/udfs/artifact")
	
	def create_udf(self, udf_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Create custom UDF."""
		return self._post("api/v1/udfs", json_data=udf_config)
	
	def update_udf(self, udf_id: str, udf_config: Dict[str, Any]) -> Dict[str, Any]:
		"""Update UDF configuration."""
		return self._put(f"api/v1/udfs/{udf_id}", json_data=udf_config)
	
	def get_udf_details(self, udf_id: str) -> Dict[str, Any]:
		"""Get detailed UDF information."""
		return self._get(f"api/v1/udfs/{udf_id}")
	
	def get_udf_artifact_details(self, artifact_id: str) -> Dict[str, Any]:
		"""Get UDF artifact details."""
		return self._get(f"api/v1/udfs/artifact/{artifact_id}")
	
	def get_udf_artifact_by_type(self, artifact_type: str) -> Dict[str, Any]:
		"""Get UDF artifacts by type."""
		return self._get(f"api/v1/udfs/artifact/type/{artifact_type}")
