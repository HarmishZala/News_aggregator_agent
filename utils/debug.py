import os
import webbrowser
from typing import Optional


def enable_langchain_debug(enabled: bool = True) -> None:
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    os.environ["LANGCHAIN_DEBUG"] = "true" if enabled else "false"


def enable_langsmith(api_key: Optional[str], project: Optional[str] = None, enabled: bool = True) -> None:
    if enabled and api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_ENDPOINT"] = os.environ.get("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        os.environ["LANGCHAIN_API_KEY"] = api_key
        if project:
            os.environ["LANGCHAIN_PROJECT"] = project
        # optional verbose logs
        os.environ["LANGCHAIN_DEBUG"] = os.environ.get("LANGCHAIN_DEBUG", "false")
    else:
        # disable
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        if "LANGCHAIN_PROJECT" in os.environ:
            del os.environ["LANGCHAIN_PROJECT"]


def open_langsmith_dashboard(project: Optional[str] = None) -> None:
    """Open LangSmith dashboard in the default browser."""
    base_url = os.getenv("LANGCHAIN_ENDPOINT", "https://smith.langchain.com")
    url = base_url.rstrip("/")
    # Best-effort project view; falls back to home
    if project:
        url = f"{url}/projects/{project}"
    webbrowser.open(url)


