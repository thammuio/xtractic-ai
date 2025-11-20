"""
Cloudera AI utility functions for environment variables and API interactions
"""
import os
import requests
from typing import Optional, List, Dict


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


def get_pdf_to_relational_workflow_url() -> Optional[str]:
    """
    Get the URL of the files-to-relational workflow application from Agent Studio
    
    Returns:
        Full URL to the files-to-relational workflow (e.g., https://subdomain.domain.com)
        Returns None if not found
        
    Raises:
        Exception: If API error occurs or credentials are missing
    """
    try:
        applications = get_applications_by_project_name_contains("Agent Studio")
        domain = get_env_var("CDSW_DOMAIN")
        
        # Find application with "files-to-relational" in the name
        for app in applications:
            app_name = app.get("name", "").lower()
            if "files-to-relational" in app_name or "pdf to relational" in app_name:
                subdomain = app.get("subdomain")
                if subdomain and domain:
                    return f"https://{subdomain}.{domain}"
        
        return None
    except Exception as e:
        raise Exception(f"Error getting files-to-relational workflow URL: {str(e)}")

