import os
import webbrowser
from typing import Optional


def enable_langchain_debug(enabled: bool = True) -> None:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_DEBUG"] = "true" if enabled else "false"


def enable_langsmith(api_key: Optional[str], project: Optional[str] = None, enabled: bool = True) -> None:
    if enabled and api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        # Map LANGSMITH_* to LANGCHAIN_* if provided
        endpoint = os.getenv("LANGSMITH_ENDPOINT") or os.environ.get("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint
        os.environ["LANGCHAIN_API_KEY"] = api_key
        project = project or os.getenv("LANGSMITH_PROJECT")
        if project:
            os.environ["LANGCHAIN_PROJECT"] = project
        # optional verbose logs
        os.environ["LANGCHAIN_DEBUG"] = os.environ.get("LANGCHAIN_DEBUG", "false")
    else:
        # disable
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        if "LANGCHAIN_PROJECT" in os.environ:
            del os.environ["LANGCHAIN_PROJECT"]


def trace_status_string() -> str:
    api_key_present = bool(os.getenv('LANGCHAIN_API_KEY') or os.getenv('LANGSMITH_API_KEY'))
    endpoint = os.getenv('LANGSMITH_ENDPOINT') or os.getenv('LANGCHAIN_ENDPOINT')
    project = os.getenv('LANGCHAIN_PROJECT') or os.getenv('LANGSMITH_PROJECT')
    tracing = os.getenv('LANGSMITH_TRACING') or os.getenv('LANGCHAIN_TRACING_V2')
    masked_key = 'SET' if api_key_present else 'MISSING'
    return f"Tracing: {tracing or 'false'} | API key: {masked_key} | Project: {project or '-'} | Endpoint: {endpoint or '-'}"


def open_langsmith_dashboard(project: Optional[str] = None) -> None:
    """Open LangSmith dashboard in the default browser.

    Notes:
    - The API endpoint (e.g., https://api.smith.langchain.com) is NOT the dashboard URL.
    - Prefer an explicit dashboard URL if provided; otherwise default to https://smith.langchain.com
    """
    dashboard_base = (
        os.getenv("LANGSMITH_DASHBOARD")
        or os.getenv("LANGCHAIN_DASHBOARD")
        or "https://smith.langchain.com"
    )
    url = dashboard_base.rstrip("/")
    if project:
        url = f"{url}/projects/{project}"
    webbrowser.open(url)


