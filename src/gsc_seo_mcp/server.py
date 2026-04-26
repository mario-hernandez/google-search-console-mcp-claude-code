"""MCP server entrypoint — registers all tools."""
from __future__ import annotations

import logging
import os

from mcp.server.fastmcp import FastMCP

from . import auth as auth_module
from .guardrails import GUARDRAIL_SUFFIX
from .tools import analytics as t_analytics
from .tools import intelligence as t_intel
from .tools import sitemaps as t_sitemaps
from .tools import sites as t_sites

logging.basicConfig(
    level=os.getenv("GSC_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)

mcp = FastMCP("gsc-seo-mcp")


def _register(fn, *, name: str | None = None):
    """Register a tool, appending the guardrail suffix to its docstring."""
    base_doc = (fn.__doc__ or "").rstrip()
    fn.__doc__ = base_doc + GUARDRAIL_SUFFIX
    return mcp.tool(name=name)(fn)


# Site & inspection
_register(t_sites.list_sites, name="list_sites")
_register(t_sites.inspect_url, name="inspect_url")

# Sitemaps
_register(t_sitemaps.list_sitemaps, name="list_sitemaps")
_register(t_sitemaps.submit_sitemap, name="submit_sitemap")

# Analytics — basics
_register(t_analytics.search_analytics, name="search_analytics")
_register(t_analytics.site_snapshot, name="site_snapshot")

# Intelligence — SEO insights
_register(t_intel.quick_wins, name="quick_wins")
_register(t_intel.traffic_drops, name="traffic_drops")
_register(t_intel.content_decay, name="content_decay")
_register(t_intel.cannibalization, name="cannibalization")
_register(t_intel.ctr_opportunities, name="ctr_opportunities")
_register(t_intel.alerts, name="alerts")


@mcp.tool()
def reauthenticate() -> dict:
    """Force re-authentication on the next API call.

    Useful when ADC credentials have changed or OAuth token has expired and
    cached state is stale. Does not delete files; just resets in-process clients.
    """
    auth_module.reset_clients()
    return {"status": "ok", "message": "Auth clients reset; next call will rebuild credentials."}


@mcp.tool()
def get_capabilities() -> dict:
    """List all tools exposed by this MCP and current auth status. Call FIRST.

    Returns the tool catalog grouped by category, plus a quick check of whether
    credentials are reachable.
    """
    auth_ok = True
    auth_error: str | None = None
    try:
        auth_module.get_webmasters().sites().list().execute()
    except Exception as e:
        auth_ok = False
        auth_error = str(e)[:300]

    return {
        "auth": {
            "ok": auth_ok,
            "error": auth_error,
            "destructive_enabled": os.getenv("GSC_ALLOW_DESTRUCTIVE") == "true",
        },
        "categories": {
            "sites": ["list_sites", "inspect_url"],
            "sitemaps": ["list_sitemaps", "submit_sitemap"],
            "analytics": ["search_analytics", "site_snapshot"],
            "intelligence": [
                "quick_wins", "traffic_drops", "content_decay",
                "cannibalization", "ctr_opportunities", "alerts",
            ],
            "meta": ["reauthenticate", "get_capabilities"],
        },
        "tip": (
            "For SEO investigation, start with `site_snapshot` for the property "
            "overview, then drill down with `quick_wins`, `traffic_drops`, and "
            "`alerts`. Use `inspect_url` for indexing diagnostics on individual pages."
        ),
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
