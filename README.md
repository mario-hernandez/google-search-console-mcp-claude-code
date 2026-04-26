# Google Search Console MCP for Claude — SEO intelligence in Python

<p align="center">
  <img src="docs/hero.png" alt="Google Search Console MCP server for Claude — SEO intelligence in Python (quick wins, cannibalization, content decay)" width="100%">
</p>

<p align="center">
  <b>Ask Claude <i>"why did my organic traffic drop last week?"</i> and get a real answer — pages auto-classified as ranking loss, CTR collapse, or demand decline, with the impressions and positions to back it up. Not a CSV dump. Not a hallucination. A diagnosis.</b>
</p>

<p align="center">
  <a href="https://github.com/mario-hernandez/google-search-console-mcp-claude-code/stargazers"><img src="https://img.shields.io/github/stars/mario-hernandez/google-search-console-mcp-claude-code?style=flat&color=10b981" alt="Stars"></a>
  <img src="https://img.shields.io/badge/python-3.11+-3776ab?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/MCP-compatible-7c3aed" alt="MCP compatible">
  <img src="https://img.shields.io/badge/no--telemetry-10b981" alt="No telemetry">
  <img src="https://img.shields.io/badge/read--only_by_default-10b981" alt="Read-only by default">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-10b981" alt="MIT"></a>
</p>

> Stop pasting Search Console screenshots into ChatGPT. Connect your GSC properties to Claude as native tools and ask the questions you actually have: which pages are decaying? where are the quick wins? which queries are cannibalizing each other?

## 30-second quickstart

```bash
# 1. Install (Python 3.11+)
pipx install git+https://github.com/mario-hernandez/google-search-console-mcp-claude-code

# 2. Authenticate (one-time, opens browser)
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly

# 3. Add to Claude Code
claude mcp add gsc-seo-mcp -- $(which gsc-seo-mcp)
```

Then ask Claude: *"List my Search Console sites and find quick wins for the last 28 days on knowingbitcoin.com."*

Works with **Claude Code**, **Claude Desktop**, **Cursor**, **Windsurf**, and any other MCP-compatible client.

## What you actually get

Three things no other GSC MCP gives you out of the box:

- 🩺 **Diagnoses, not data dumps** — `traffic_drops` doesn't return rows; it returns pages classified as `ranking_loss` / `ctr_collapse` / `demand_decline` with the diagnostic numbers attached.
- 🔍 **Anti-hallucination guardrails** — every response is wrapped with `_meta` provenance (source, site_url, period, fetched_at). Your agent literally cannot make up the numbers when reporting to clients.
- 🛡️ **Read-only by default** — destructive operations (sitemap submission, etc.) require an explicit `GSC_ALLOW_DESTRUCTIVE=true` flag. Safe to point at your production properties.

## Real example — `traffic_drops` output

Ask Claude: *"Why did sofrologia.com lose traffic this month?"*

```json
[
  {
    "page": "https://www.sofrologia.com/curso-sofrologia/",
    "diagnosis": "ranking_loss",
    "current":  { "clicks": 47, "impressions": 1820, "ctr": 0.026, "position": 14.2 },
    "previous": { "clicks": 198, "impressions": 1910, "ctr": 0.103, "position": 6.8 },
    "click_delta": -151,
    "position_delta": 7.4
  },
  {
    "page": "https://www.sofrologia.com/que-es-sofrologia/",
    "diagnosis": "ctr_collapse",
    "current":  { "clicks": 89, "impressions": 4200, "ctr": 0.021, "position": 3.1 },
    "previous": { "clicks": 312, "impressions": 4350, "ctr": 0.072, "position": 3.0 },
    "click_delta": -223,
    "position_delta": 0.1
  }
]
```

Claude can now *explain* the drop — page #1 lost 7 ranking positions, page #2 held its position but its CTR collapsed (likely a SERP feature ate the click). Two fundamentally different problems, two different fixes.

## SEO intelligence tools

<details open>
<summary><b>The 6 diagnostic tools</b></summary>

| Tool | What it surfaces |
|------|------------------|
| `quick_wins` | Queries in positions 4-15 ranked by `impressions × CTR-gap-to-pos-3`. Finds the keywords one push away from the top. |
| `traffic_drops` | Pages losing traffic, classified as `ranking_loss` / `ctr_collapse` / `demand_decline` / `mixed`. |
| `content_decay` | Pages with **monotonic decline** across 3 consecutive 30-day windows. Filters single-week noise. |
| `cannibalization` | Queries where ≥2 pages on your site compete with each other in the SERP. |
| `ctr_opportunities` | Pages whose CTR is far below the expected CTR for their position. Title/meta candidates. |
| `alerts` | Position drops, CTR collapses, click drops, disappeared queries — deduped by severity. |

</details>

<details>
<summary><b>The 8 foundation tools</b></summary>

| Tool | What it does |
|------|--------------|
| `list_sites` | Verified properties + permission level + property type |
| `inspect_url` | URL Inspection API — index status, canonical, mobile, rich results |
| `list_sitemaps` | Sitemaps with errors / warnings / last-submitted |
| `submit_sitemap` | Submit a sitemap (gated by `GSC_ALLOW_DESTRUCTIVE=true`) |
| `search_analytics` | Custom Search Analytics query (queries / pages / countries / devices) |
| `site_snapshot` | Aggregated totals for last N days vs prior period |
| `get_capabilities` | Tool catalog + auth status (call this first) |
| `reauthenticate` | Reset in-process auth clients |

</details>

## Compared to other Google Search Console MCP servers

There are four serious open-source GSC MCPs — they're all good and you should pick the one that fits your workflow.

| You should use… | If you want… |
|-----------------|--------------|
| [**Amin Forou's mcp-gsc**](https://github.com/AminForou/mcp-gsc) (733⭐, Python) | The most polished general-purpose GSC bridge with raw `search_analytics` queries. Pick if you're building your own SEO logic on top. |
| [**Suganthan's GSC MCP**](https://github.com/Suganthan-Mohanadasan/Suganthans-GSC-MCP) (TypeScript) | Maximum tool surface (~30 tools including SERP feature analysis, schema audits). Pick if you're a TypeScript shop and want every drilldown. |
| [**surendranb's gsc-mcp**](https://github.com/surendranb/google-search-console-mcp) (Python) | A 200-line FastMCP starter you can fork and extend. Pick if you want minimal scaffolding. |
| [**acamolese's mcp**](https://github.com/acamolese/google-search-console-mcp) (Python) | Polished printable HTML reports for clients with Chart.js. Pick if you deliver standalone audits. |
| **This MCP** | **Diagnostic SEO logic in Python with anti-hallucination guardrails baked in.** Pick if your agent reports to clients and you can't afford a hallucinated CTR number. |

This MCP started as a security-audited synthesis of the four above — credit at the bottom of this README.

## Authentication

### Default — Application Default Credentials (recommended)

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/webmasters.readonly
```

The authenticated Google account must be a verified user/owner of each Search Console property you want to query.

<details>
<summary><b>Advanced auth methods</b> — OAuth user flow / Service account</summary>

### OAuth user flow (interactive)

Create a Desktop OAuth client in your Google Cloud project, then:

```bash
export GSC_OAUTH_CLIENT_FILE=/path/to/client_secret.json
```

The first call opens a browser; the token is cached at `~/Library/Application Support/gsc-seo-mcp/token.json` (macOS) or the equivalent `XDG_CONFIG_HOME` location.

### Service account (headless servers)

```bash
export GSC_SERVICE_ACCOUNT_FILE=/path/to/sa-key.json
```

The service account email must be added as a user in each Search Console property.

</details>

## Configure with your client

<details open>
<summary><b>Claude Code</b></summary>

```bash
claude mcp add gsc-seo-mcp -- $(which gsc-seo-mcp)
```

Or manually in `~/.claude.json`:

```json
{
  "mcpServers": {
    "gsc-seo-mcp": {
      "type": "stdio",
      "command": "gsc-seo-mcp"
    }
  }
}
```

</details>

<details>
<summary><b>Claude Desktop</b></summary>

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "gsc-seo-mcp": {
      "command": "gsc-seo-mcp"
    }
  }
}
```

</details>

<details>
<summary><b>Cursor / Windsurf / Zed</b></summary>

In your MCP config:

```json
{
  "gsc-seo-mcp": { "command": "gsc-seo-mcp" }
}
```

</details>

<details>
<summary><b>Environment variables</b></summary>

| Var | Default | Purpose |
|-----|---------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | gcloud ADC default | ADC file path |
| `GSC_OAUTH_CLIENT_FILE` | — | Desktop OAuth client JSON |
| `GSC_SERVICE_ACCOUNT_FILE` | — | Service account key path |
| `GSC_ALLOW_DESTRUCTIVE` | `false` | Enables sitemap submission and write-scope OAuth |
| `GSC_CTR_BENCHMARKS` | conservative defaults | Comma-separated 10 floats overriding per-position expected CTR |
| `GSC_LOG_LEVEL` | `INFO` | Python log level |

</details>

## FAQ

**Why another GSC MCP?** Because no other GSC MCP returns provenance metadata on every response. When your agent reports a CTR drop to a client, you need to be able to point at the exact API call, site URL, and date range that produced the number. `_meta` makes that automatic.

**Does this work with non-Claude clients?** Yes — anything that speaks MCP (Cursor, Windsurf, Zed, custom agents). It's a standard FastMCP server over stdio.

**Can I use this on a property where I'm not the verified owner?** Yes, as long as the authenticated Google account has at least Restricted user access in Search Console.

## Credits

Independent re-implementation that synthesizes the strongest ideas from four open-source projects, all of which were security-audited and found clean before being studied:

- [Suganthan-Mohanadasan/Suganthans-GSC-MCP](https://github.com/Suganthan-Mohanadasan/Suganthans-GSC-MCP) — diagnostic SEO logic (quick-wins scoring, traffic-drop tri-classification, content-decay 3-window check, alerts dedup-by-severity)
- [AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc) — LLM-oriented error messages, destructive-flag gating, capability discovery
- [acamolese/google-search-console-mcp](https://github.com/acamolese/google-search-console-mcp) — three-tier credential cascade, scope minimization
- [surendranb/google-search-console-mcp](https://github.com/surendranb/google-search-console-mcp) — minimal FastMCP boilerplate

If those projects fit your workflow better, use them — they're great in their own right.

## License

MIT — see [LICENSE](LICENSE).

---

<p align="center">
  <i>If this saved you a Looker Studio dashboard, give it a ⭐.</i>
</p>
