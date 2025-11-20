"""
Cloudera AI utility functions for environment variables and API interactions
"""
import os
import json
import requests
from typing import Optional, List, Dict
import cmlapi


def get_env_var(var_name: str, default: Optional[str] = None) -> str:
    """
    Get environment variable value
    
    Args:
        var_name: Name of the environment variable
        default: Default value if variable is not set
        
    Returns:
        Environment variable value
        
    Raises:
        Exception: If variable is not set and no default provided
    """
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        raise Exception(f"Environment variable {var_name} not set")


def get_cloudera_credentials() -> dict:
    """
    Get Cloudera AI credentials from environment variables
    
    Returns:
        Dictionary containing CDSW domain, API key, and project ID
    """
    return {
        "domain": get_env_var("CDSW_DOMAIN"),
        "api_key": get_env_var("CDSW_APIV2_KEY"),
        "project_id": get_env_var("CDSW_PROJECT_ID"),
        "workspace_domain": f"https://{get_env_var('CDSW_DOMAIN')}"
    }


def get_cml_client() -> cmlapi.CMLServiceApi:
    """
    Create and return a CML API client
    
    Returns:
        Configured CML API client
    """
    credentials = get_cloudera_credentials()
    return cmlapi.default_client(
        credentials["workspace_domain"],
        credentials["api_key"]
    )


def get_app_id(cml_client: cmlapi.CMLServiceApi, project_id: str, app_name: str) -> str:
    """
    Get application ID by name
    
    Args:
        cml_client: CML API client
        project_id: Project ID
        app_name: Name of the application
        
    Returns:
        Application ID
        
    Raises:
        Exception: If API error occurs
    """
    try:
        app_list = cml_client.list_applications(
            project_id,
            search_filter=json.dumps({"name": app_name})
        )
        if not app_list.applications:
            raise Exception(f"Application '{app_name}' not found")
        return app_list.applications[0].id
    except cmlapi.exceptions.ApiException as e:
        raise Exception(f"API error occurred while getting app ID: {str(e)}")


def get_workflow_endpoint() -> str:
    """
    Get the deployed workflow endpoint URL
    
    Returns:
        Workflow endpoint URL
    """
    # Try to get from environment first
    workflow_url = get_env_var("DEPLOYED_WORKFLOW_URL", None)
    
    if not workflow_url:
        # Construct from CDSW_DOMAIN if available
        try:
            domain = get_env_var("CDSW_DOMAIN")
            # This is a fallback - actual workflow ID should be in env
            workflow_url = f"https://{domain}"
        except Exception:
            # Use default hardcoded URL as last resort
            workflow_url = "https://workflow-0421b0de-eec0-4dab-9a72-00e31453cf14.ml-d248e68a-04a.se-sandb.a465-9q4k.cloudera.site"
    
    return workflow_url


def get_cloudera_headers() -> dict:
    """
    Get headers for Cloudera API requests
    
    Returns:
        Dictionary containing authorization and content-type headers
    """
    api_key = get_env_var("CDSW_APIV2_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


def setup_applications(api_subdomain: str = "xtracticai-api", ui_subdomain: str = "xtracticai-ui") -> dict:
    """
    Setup and configure API and UI applications
    
    Args:
        api_subdomain: Subdomain for API application
        ui_subdomain: Subdomain for UI application
        
    Returns:
        Dictionary containing setup results
    """
    try:
        credentials = get_cloudera_credentials()
        cml_client = get_cml_client()
        project_id = credentials["project_id"]
        
        # Setup API application
        api_app_id = get_app_id(cml_client, project_id, "API for Chatbot")
        update_and_restart_app(cml_client, project_id, api_app_id, api_subdomain)
        
        # Setup UI application
        ui_app_id = get_app_id(cml_client, project_id, "Frontend UI")
        update_and_restart_app(cml_client, project_id, ui_app_id, ui_subdomain)
        
        return {
            "success": True,
            "api_app_id": api_app_id,
            "ui_app_id": ui_app_id,
            "api_subdomain": api_subdomain,
            "ui_subdomain": ui_subdomain,
            "message": "Applications configured and restarted successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to setup applications"
        }


def get_all_cloudera_env_vars() -> dict:
    """
    Get all Cloudera-related environment variables
    
    Returns:
        Dictionary containing all available Cloudera environment variables
    """
    env_vars = {}
    cloudera_keys = [
        "CDSW_DOMAIN",
        "CDSW_APIV2_KEY",
        "CDSW_PROJECT_ID",
        "CDSW_APP_PORT",
        "DEPLOYED_WORKFLOW_URL",
        "CLOUDERA_API_URL",
        "CLOUDERA_API_KEY",
        "CLOUDERA_WORKSPACE_ID"
    ]
    
    for key in cloudera_keys:
        try:
            env_vars[key] = get_env_var(key)
        except Exception:
            env_vars[key] = None
    
    return env_vars


def get_project_id_by_name_contains(name_contains: str) -> Optional[str]:
    """
    Get project ID where the project name contains the specified string
    Supports patterns like "Agent Studio", "Agent Studio - suri", etc.
    
    Args:
        name_contains: String to search for in project names (case-insensitive)
        
    Returns:
        Project ID if found, None otherwise
        
    Raises:
        Exception: If API error occurs or credentials are missing
    """
    try:
        import re
        
        domain = get_env_var("CDSW_DOMAIN")
        api_key = get_env_var("CDSW_APIV2_KEY")
        
        # Ensure domain has protocol
        if not domain.startswith("http"):
            domain = f"https://{domain}"
        
        url = f"{domain}/api/v2/projects"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        projects = data.get("projects", [])
        
        # Create a regex pattern that matches the name_contains at the start
        # This will match "Agent Studio", "Agent Studio - suri", "Agent Studio - anything", etc.
        pattern = re.compile(rf"^{re.escape(name_contains)}(\s*-\s*.*)?$", re.IGNORECASE)
        
        for project in projects:
            project_name = project.get("name", "")
            if pattern.match(project_name):
                return project.get("id")
        
        return None
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API error occurred while fetching projects: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching project ID: {str(e)}")


def get_all_projects() -> List[Dict]:
    """
    Get all projects from Cloudera AI
    
    Returns:
        List of project dictionaries
        
    Raises:
        Exception: If API error occurs or credentials are missing
    """
    try:
        domain = get_env_var("CDSW_DOMAIN")
        api_key = get_env_var("CDSW_APIV2_KEY")
        
        # Ensure domain has protocol
        if not domain.startswith("http"):
            domain = f"https://{domain}"
        
        url = f"{domain}/api/v2/projects"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        return data.get("projects", [])
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API error occurred while fetching projects: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching projects: {str(e)}")


def get_applications_by_project_name_contains(name_contains: str) -> List[Dict]:
    """
    Get all applications from projects where the name contains the specified string
    
    Args:
        name_contains: String to search for in project names (case-insensitive)
        
    Returns:
        List of application dictionaries with project info
        
    Raises:
        Exception: If API error occurs or credentials are missing
    """
    try:
        domain = get_env_var("CDSW_DOMAIN")
        api_key = get_env_var("CDSW_APIV2_KEY")
        
        # First, get the project ID
        project_id = get_project_id_by_name_contains(name_contains)
        
        if not project_id:
            return []
        
        # Ensure domain has protocol
        if not domain.startswith("http"):
            domain = f"https://{domain}"
        
        # Get applications for the project
        url = f"{domain}/api/v2/projects/{project_id}/applications"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        applications = data.get("applications", [])
        
        # Add project_id to each application for reference
        for app in applications:
            app["project_id"] = project_id
        
        return applications
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"API error occurred while fetching applications: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching applications: {str(e)}")


def get_agent_studio_applications() -> List[Dict]:
    """
    Get all applications from Agent Studio project
    Convenience function that searches for projects with "Agent Studio" in the name
    
    Returns:
        List of application dictionaries from Agent Studio project
        
    Raises:
        Exception: If API error occurs or credentials are missing
    """
    return get_applications_by_project_name_contains("Agent Studio")

