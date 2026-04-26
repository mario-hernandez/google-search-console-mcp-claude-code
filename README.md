# GSC SEO MCP

<p align="center">
  <img src="docs/hero.png" alt="GSC SEO MCP — Search Console intelligence for AI assistants" width="100%">
</p>

<p align="center">
  <b>Google Search Console as a Model Context Protocol server — with SEO intelligence built in.</b>
</p>

<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/python-3.11+-3776ab?logo=python&logoColor=white" alt="Python 3.11+"></a>
  <a href="#"><img src="https://img.shields.io/badge/MCP-1.2+-7c3aed" alt="MCP 1.2+"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-10b981" alt="MIT"></a>
  <a href="#"><img src="https://img.shields.io/badge/status-alpha-f59e0b" alt="alpha"></a>
</p>

---

## Why?

Google Search Console answers the questions that actually matter for SEO — *which queries are losing rankings? which pages are decaying? where are the quick wins?* — but the dashboard buries them under raw data. Existing GSC MCPs hand back rows; this one hands back **diagnoses**.

Inspired by manual audits of four open-source GSC MCPs, this server cherry-picks the strongest ideas from each:

- **Diagnostic SEO logic** ported to Python (concepts adapted from [Suganthan-Mohanadasan/Suganthans-GSC-MCP](https://github.com/Suganthan-Mohanadasan/Suganthans-GSC-MCP))
- **LLM-friendly error messages + destructive-flag gating** ([AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc))
- **Minimal FastMCP skeleton** ([surendranb/google-search-console-mcp](https://github.com/surendranb/google-search-console-mcp))
- **Auth-cascade pattern** ([acamolese/google-search-console-mcp](https://github.com/acamolese/google-search-console-mcp))

…all with a modular layout, anti-hallucination guardrails, and `_meta` provenance on every response.

## Tools

### Site & inspection

| Tool | What it does |
|------|--------------|
| `list_sites` | Verified properties + permission level + property type |
| `inspect_url` | URL Inspection API — index status, canonical, mobile, rich results |

### Sitemaps

| Tool | What it does |
|------|--------------|
| `list_sitemaps` | Sitemaps with errors/warnings/last-submitted |
| `submit_sitemap` | Submit a sitemap (requires `GSC_ALLOW_DESTRUCTIVE=true`) |

### Analytics

| Tool | What it does |
|------|--------------|
| `search_analytics` | Custom Search Analytics query (queries / pages / countries / devices) |
| `site_snapshot` | Aggregated totals for last N days vs prior period |

### Intelligence

| Tool | What it does |
|------|--------------|
| `quick_wins` | Queries in positions 4–15 ranked by `impressions × CTR-gap-to-pos-3` |
| `traffic_drops` | Pages losing traffic, **classified** as `ranking_loss` / `ctr_collapse` / `demand_decline` |
| `content_decay` | Pages with **monotonic decline** across 3 consecutive 30-day windows |
| `cannibalization` | Queries where ≥2 pages on the same site compete |
| `ctr_opportunities` | Pages whose CTR is far below expected for their position |
| `alerts` | Position drops, CTR collapses, click drops, disappeared entities — deduped by severity |

### Meta

| Tool | What it does |
|------|--------------|
| `get_capabilities` | Tool catalog + auth status (call this first) |
| `reauthenticate` | Reset in-process auth clients |

## Install

```bash
git clone https://github.com/mario-hernandez/gsc-seo-mcp.git
cd gsc-seo-mcp
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Authentication

Three methods, tried in this order:

### 1. Application Default Credentials (recommended for personal use)

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
```

### 2. OAuth user flow (interactive)

Create a Desktop OAuth client in your Google Cloud project and:

```bash
export GSC_OAUTH_CLIENT_FILE=/path/to/client_secret.json
```

The first call opens a browser; the token is cached at `~/Library/Application Support/gsc-seo-mcp/token.json` (macOS) or the equivalent `XDG_CONFIG_HOME` location.

### 3. Service account (headless)

```bash
export GSC_SERVICE_ACCOUNT_FILE=/path/to/sa-key.json
```

The service account email must be added as a user in each Search Console property.

## Configure with Claude Code

Add to `~/.claude.json` under `mcpServers`:

```json
{
  "gsc-seo-mcp": {
    "type": "stdio",
    "command": "/absolute/path/to/.venv/bin/gsc-seo-mcp",
    "args": [],
    "env": {
      "GOOGLE_APPLICATION_CREDENTIALS": "/Users/you/.config/gcloud/application_default_credentials.json"
    }
  }
}
```

Restart Claude Code, then ask: *"List my Search Console sites and run a snapshot for the last 28 days."*

## Configure with Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gsc-seo-mcp": {
      "command": "/absolute/path/to/.venv/bin/gsc-seo-mcp"
    }
  }
}
```

## Environment variables

| Var | Default | Purpose |
|-----|---------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | gcloud ADC default | ADC file path |
| `GSC_OAUTH_CLIENT_FILE` | — | Desktop OAuth client JSON |
| `GSC_SERVICE_ACCOUNT_FILE` | — | Service account key path |
| `GSC_ALLOW_DESTRUCTIVE` | `false` | Enables sitemap submission and write-scope OAuth |
| `GSC_CTR_BENCHMARKS` | conservative defaults | Comma-separated 10 floats overriding per-position expected CTR |
| `GSC_LOG_LEVEL` | `INFO` | Python log level |

## Design principles

- **Read-only by default.** Destructive operations require a flag.
- **Provenance always included.** Every response is wrapped in `{ "data": ..., "_meta": { source, site_url, period, fetched_at } }`. The LLM can cite where each number came from.
- **Anti-hallucination guardrails.** Every tool docstring ends with a reminder not to extrapolate beyond what was returned.
- **Diagnoses, not data dumps.** Intelligence tools classify findings (`ranking_loss` vs `ctr_collapse` vs `demand_decline`) rather than handing the LLM thousands of rows to summarize.
- **Lag-aware date helpers.** All "last N days" defaults end at `today - 3` to avoid GSC's reporting lag.

## Credits & inspiration

Independent re-implementation of ideas from:
- [Suganthan-Mohanadasan/Suganthans-GSC-MCP](https://github.com/Suganthan-Mohanadasan/Suganthans-GSC-MCP) — diagnostic SEO logic (quick-wins scoring, traffic-drop tri-classification, content-decay 3-window check, alerts dedup-by-severity)
- [AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc) — LLM-oriented error messages, destructive-flag gating, capability discovery as first-call entry
- [acamolese/google-search-console-mcp](https://github.com/acamolese/google-search-console-mcp) — three-tier credential cascade, scope minimization
- [surendranb/google-search-console-mcp](https://github.com/surendranb/google-search-console-mcp) — minimal FastMCP boilerplate

All of those are great projects in their own right — pick whichever matches your stack.

## Security notes

- **No telemetry.** Zero outbound traffic to anything other than `googleapis.com` / `accounts.google.com` / `oauth2.googleapis.com`.
- **No credentials in the repo.** `.gitignore` excludes `*.json` by default.
- **Read-only OAuth scope** unless `GSC_ALLOW_DESTRUCTIVE=true`.

## License

MIT — see [LICENSE](LICENSE).
