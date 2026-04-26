"""Authentication for Google Search Console API.

Resolution order (first match wins):
  1. ADC — `GOOGLE_APPLICATION_CREDENTIALS` env or default `gcloud` ADC file.
     Must include scope `webmasters.readonly`.
  2. OAuth user flow — `GSC_OAUTH_CLIENT_FILE` points to a Desktop client JSON.
     Token cached at `<user_config_dir>/gsc-seo-mcp/token.json`.
  3. Service account — `GSC_SERVICE_ACCOUNT_FILE` for headless setups.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

from google.auth import default as google_auth_default
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as SACredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from platformdirs import user_config_dir

log = logging.getLogger(__name__)

SCOPES_READ = ["https://www.googleapis.com/auth/webmasters.readonly"]
SCOPES_WRITE = ["https://www.googleapis.com/auth/webmasters"]

_searchconsole_service: Any = None
_webmasters_service: Any = None


def _config_dir() -> Path:
    p = Path(user_config_dir("gsc-seo-mcp"))
    p.mkdir(parents=True, exist_ok=True)
    return p


def _scopes() -> list[str]:
    return SCOPES_WRITE if os.getenv("GSC_ALLOW_DESTRUCTIVE") == "true" else SCOPES_READ


def _from_adc() -> Any | None:
    try:
        creds, project = google_auth_default(scopes=_scopes())
        log.info("Using ADC credentials (project=%s)", project)
        return creds
    except Exception as e:
        log.debug("ADC unavailable: %s", e)
        return None


def _from_service_account() -> Any | None:
    sa_path = os.getenv("GSC_SERVICE_ACCOUNT_FILE")
    if not sa_path or not Path(sa_path).exists():
        return None
    log.info("Using service account at %s", sa_path)
    return SACredentials.from_service_account_file(sa_path, scopes=_scopes())


def _from_oauth_flow() -> Any | None:
    client_file = os.getenv("GSC_OAUTH_CLIENT_FILE")
    if not client_file or not Path(client_file).exists():
        return None

    token_path = _config_dir() / "token.json"
    creds: Credentials | None = None
    if token_path.exists():
        try:
            creds = Credentials.from_authorized_user_info(
                json.loads(token_path.read_text()), _scopes()
            )
        except Exception as e:
            log.warning("Could not load cached token, re-authenticating: %s", e)
            creds = None

    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            creds = None

    if not creds:
        flow = InstalledAppFlow.from_client_secrets_file(client_file, _scopes())
        creds = flow.run_local_server(port=0, open_browser=True)
        token_path.write_text(creds.to_json())
        token_path.chmod(0o600)

    return creds


def _build_creds() -> Any:
    creds = _from_adc() or _from_service_account() or _from_oauth_flow()
    if creds is None:
        raise RuntimeError(
            "No Google credentials found. Set up ADC with `gcloud auth application-default "
            "login --scopes=https://www.googleapis.com/auth/webmasters.readonly`, or set "
            "GSC_OAUTH_CLIENT_FILE / GSC_SERVICE_ACCOUNT_FILE."
        )
    return creds


def get_searchconsole():
    """Returns a Search Console v1 client (URL Inspection API lives here)."""
    global _searchconsole_service
    if _searchconsole_service is None:
        _searchconsole_service = build(
            "searchconsole", "v1", credentials=_build_creds(), cache_discovery=False
        )
    return _searchconsole_service


def get_webmasters():
    """Returns a Webmasters v3 client (Search Analytics, sitemaps, sites)."""
    global _webmasters_service
    if _webmasters_service is None:
        _webmasters_service = build(
            "webmasters", "v3", credentials=_build_creds(), cache_discovery=False
        )
    return _webmasters_service


def reset_clients() -> None:
    """Force rebuild on next access — used by `reauthenticate` tool."""
    global _searchconsole_service, _webmasters_service
    _searchconsole_service = None
    _webmasters_service = None
