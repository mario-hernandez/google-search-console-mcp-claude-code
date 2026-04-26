# Why your AI SEO agent is lying to you (and how `_meta` provenance fixes it)

> Status: DRAFT — para revisión de Mario antes de publicar en dev.to + cross-post LinkedIn.

---

Last week I asked Claude to summarize my Google Search Console data using a popular MCP server. It told me my CTR on `/curso-sofrologia/` had dropped 47% over the last 28 days.

That was a confident, specific, useful number.

It was also wrong.

The actual drop, when I cross-checked the GSC dashboard manually, was 12%. The agent had averaged across the wrong date range, then anchored to a number it had cited two messages earlier, then "interpolated" something that sounded reasonable.

If I had pasted that into a client report, I would have looked like an idiot. Or worse — like someone who fabricates data.

This is the dirty secret of AI-assisted SEO right now: **agents hallucinate metrics**, and the architecture of most MCP servers makes it impossible to detect when they do.

## How agents lie about your data

There are three failure modes I've seen, in increasing order of badness:

**1. Mid-conversation drift.** The agent fetches real data on turn 1. By turn 5 — after a few summarizations and synthesis steps — the numbers have shifted by 5-20%. You can't see this unless you re-query. The model isn't being malicious, it's compressing context, and metrics are the first thing to go.

**2. Cross-query contamination.** The agent runs `query: "last 28 days"` and `query: "last 7 days"` in sequence, then composes a response that mixes them. Both numbers are real. The combined sentence is fiction.

**3. Pure fabrication.** The agent never queries at all because it "remembers" data from a similar property mentioned earlier. This happens more often than you'd think with multi-property workflows ("compare knowingbitcoin.com and supera.dev").

## Why this is an architecture problem, not a prompting problem

You can't prompt your way out of this. "Be careful with numbers" doesn't survive the third turn. "Cite your sources" doesn't help if there's nothing structured to cite.

The fix has to be at the data layer.

When a tool returns:

```json
{ "clicks": 47, "impressions": 1820, "ctr": 0.026, "position": 14.2 }
```

…the agent has no anchor. Those numbers float free in the conversation. By turn 7 they could be anything.

But when a tool returns:

```json
{
  "data": { "clicks": 47, "impressions": 1820, "ctr": 0.026, "position": 14.2 },
  "_meta": {
    "source": "webmasters.searchanalytics.query (snapshot)",
    "site_url": "https://www.sofrologia.com/",
    "period": { "start": "2026-03-29", "end": "2026-04-25" },
    "fetched_at": "2026-04-26T14:43:14.988Z"
  }
}
```

…you can write a system prompt that says "always cite the `_meta.period` and `_meta.fetched_at` when reporting numbers." Now the agent has somewhere to anchor. It quotes 47 clicks **for sofrologia.com between 2026-03-29 and 2026-04-25**. If it later contradicts itself, the contradiction is visible to the human reading the output.

This is not a perfect fix. The agent can still ignore the `_meta`. But it makes the right behavior the easy behavior — and it makes audit trails possible.

## The MCP I built to test this

I wrote [`google-search-console-mcp-claude-code`](https://github.com/mario-hernandez/google-search-console-mcp-claude-code), a Python MCP server that wraps Search Console with `_meta` provenance on every response, plus a layer of diagnostic tools (so the agent gets *diagnoses* like "ranking_loss" or "ctr_collapse" instead of raw CSV-style dumps it has to summarize itself).

```bash
pipx install git+https://github.com/mario-hernandez/google-search-console-mcp-claude-code
```

Tools include:

- `traffic_drops` — pages losing traffic auto-classified as `ranking_loss` / `ctr_collapse` / `demand_decline`
- `quick_wins` — queries one rank-push away from the top, scored by impressions × CTR-gap
- `content_decay` — pages with monotonic decline across 3 consecutive 30-day windows
- `cannibalization` — queries where ≥2 of your pages compete

And every response carries `_meta`.

## What I'd love to see become standard

Three things I think the MCP ecosystem would benefit from adopting as soft conventions:

1. **`_meta` provenance on every tool response** — source, query parameters, fetched_at timestamp.
2. **Diagnoses, not dumps.** Tools that classify findings (`severity: "critical"`, `diagnosis: "ranking_loss"`) reduce the LLM's summarization burden, which reduces drift.
3. **Read-only by default.** Destructive operations behind explicit flags. Self-evident, but only ~half the GSC MCPs I audited do this correctly.

If you build MCP servers — for Search Console or anything else — try wrapping your responses in `_meta`. The first time you see your agent spontaneously cite a date range it would have hallucinated otherwise, it's hard to go back.

## Try it / break it

Repo: https://github.com/mario-hernandez/google-search-console-mcp-claude-code

Issues, ideas, and "your `_meta` doesn't actually fix this case" replies welcome.

---

*Mario Hernández builds open-source tools for SEO and self-hosted analytics. Follow on [GitHub](https://github.com/mario-hernandez).*
