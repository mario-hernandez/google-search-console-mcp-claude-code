# ⚠️ This repo has been superseded

This MCP has been **unified with the GA4 MCP** into a single comprehensive Google SEO suite — including five **cross-platform tools** that connect Search Console with Analytics 4 (GSC↔GA4 journey, opportunity matrix, traffic health check, revenue attribution, full landing page diagnosis).

## 👉 New repo: [`google-seo-mcp-claude-code`](https://github.com/mario-hernandez/google-seo-mcp-claude-code)

The new MCP includes everything this one did (with prefixed `gsc_*` tool names) plus the five cross-platform tools that are only possible with unified auth.

## Migration

```bash
pipx uninstall gsc-seo-mcp
pipx install git+https://github.com/mario-hernandez/google-seo-mcp-claude-code
```

Update your Claude config from `gsc-seo-mcp` to `google-seo-mcp`.

Tool names are prefixed in the new MCP:
- `quick_wins` → `gsc_quick_wins`
- `traffic_drops` → `gsc_traffic_drops`
- `content_decay` → `gsc_content_decay`
- (etc.)

This repo is kept for historical reference only and is no longer maintained.
