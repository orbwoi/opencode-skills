---
name: gpt-researcher
description: Research skill for AI agents. Use this skill when you need to conduct web searches or deep research. Provides access to MCP tools for quick searches and deep research with automatic HTML-to-Markdown conversion. All outputs are clean Markdown-formatted text suitable for LLM consumption.
---

# GPT Researcher Skill

## CRITICAL: Know Your Role

**You may be in one of two contexts:**

| Context | How You Got Here | Your Role | What To Do |
|---------|------------------|-----------|------------|
| **Main Agent** | User asked you a question requiring research | Coordinator | Delegate to researcher sub-agent via Task tool |
| **Researcher Sub-Agent** | You were spawned by Task tool with `subagent_type: "researcher"` | Researcher | Call MCP tools directly, synthesize results, return summary |

**If you ARE the researcher sub-agent:**
- DO NOT delegate further - YOU are the researcher
- DO NOT use webfetch - USE THE MCP TOOLS provided
- Call `gpt_researcher_quick_search` or `gpt-researcher_deep_research` directly
- Synthesize findings and return a clean summary to the main agent

---

## Tool Reference

### MCP Tools Available

| Tool | Use Case | When to Use |
|------|----------|-------------|
| `gpt-researcher_quick_search` | Fast web search | Simple facts, current values, quick lookups |
| `gpt-researcher_deep_research` | Comprehensive research | Any topic needing multiple sources, analysis, synthesis |

### DO NOT Use These (for initial research)

| Tool | Why Not |
|------|---------|
| `webfetch` | For initial searches - use MCP tools instead |

### When webfetch IS Appropriate

| Scenario | Example |
|----------|---------|
| Fetching a specific URL from search results | "Get more details from https://deepinfra.com/pricing found in the search" |
| Checking a known page | "Check the docs at https://docs.example.com/api" |
| Following up on a specific link | "Read the full article at [URL from previous search]" |

**Rule of thumb:**
- Need to FIND information → Use MCP tools (`quick_search`, `deep_research`)
- Have a specific URL to read → `webfetch` is fine

---

## For Main Agent: When to Delegate

**From the main agent context, delegate research to the researcher sub-agent:**

```
Task(
  subagent_type: "researcher",
  prompt: "Research [topic]. Focus on [specific aspects]. Return [desired format]."
)
```

**Example:**
```
Task(
  subagent_type: "researcher",
  prompt: "Research GLM-5 hosting providers in USA. Compare pricing, privacy compliance, and context window support. Return a comparison table with top 5 recommendations."
)
```

---

## For Researcher Sub-Agent: How to Research

**You are the researcher. Do the work yourself. Do NOT delegate.**

### Step 1: Choose Your Tool

| Need | Tool |
|------|------|
| Quick fact (single value, definition, current price) | `gpt-researcher_quick_search` |
| Any research (multi-faceted, comparison, analysis) | `gpt-researcher_deep_research` |

### Step 2: Call the Tool Directly

**Quick search example:**
```
gpt-researcher_quick_search(query="GLM-5 API providers USA 2026")
```

**Deep research example:**
```
gpt-researcher_deep_research(query="Compare GLM-5 hosting providers in USA with focus on pricing, privacy compliance (ZDR, no-training policies), and context window sizes")
```

### Step 3: Synthesize and Return

After getting results:
1. Read the returned context
2. Synthesize the key findings
3. Return a clean summary (1k-3k tokens) to the main agent
4. Do NOT return 50k tokens of raw context

**Your response should be structured like:**
```markdown
## Summary
[Brief overview]

## Key Findings
- Finding 1
- Finding 2
- Finding 3

## Details
[Relevant details organized by topic]

## Sources
- URL 1
- URL 2
```

---

## Query Best Practices

### Good Queries

| Query | Why It Works |
|-------|--------------|
| "GLM-5 hosting providers USA with zero data retention 2026" | Specific, scoped, time-referenced |
| "Cloudflare Workers AI pricing per million tokens February 2026" | Exact metric, time-sensitive |
| "compare DeepInfra vs Fireworks vs Together AI for GLM-4" | Comparison, specific models |

### Bad Queries

| Query | Why It Fails |
|-------|--------------|
| "tell me about AI" | Too broad |
| "what's new" | No scope, no specificity |
| "cheap AI" | No context, no comparison |

---

## Token Expectations

| Tool | Input Tokens | Output Tokens | Total Context Impact |
|------|--------------|---------------|----------------------|
| `quick_search` | ~100 | ~500 | Low (~600) |
| `deep_research` | ~200 | 10k-50k | High (must synthesize) |
| Synthesized report | - | 1k-3k | What you should return |

---

## Example: Researcher Sub-Agent Session

**You receive this prompt:**
> "Research GLM-5 providers in USA with privacy compliance. Return top 5 with pricing."

**You ARE the researcher. You do this:**

1. Call `gpt-researcher_deep_research(query="GLM-5 API hosting providers USA privacy compliance zero data retention pricing comparison")`

2. Read the returned context (10k-50k tokens)

3. Synthesize into a clean summary:

```markdown
## Top 5 GLM-5 Providers in USA (Privacy-Focused)

| Provider | Price/1M Tokens | ZDR | No-Training | Notes |
|----------|-----------------|-----|-------------|-------|
| DeepInfra | $0.14 | ✅ | ✅ | Best value |
| Together AI | $0.20 | ✅ | ✅ | Enterprise support |
| ...

## Recommendation
DeepInfra offers the best value for GLM-5 with strong privacy guarantees...

## Sources
- https://deepinfra.com/pricing
- https://together.ai/privacy
```

4. Return ONLY the synthesized summary (not the raw context)

---

## Red Flags

| ❌ Wrong Approach | ✅ Correct Approach |
|-------------------|---------------------|
| "I'll use webfetch to get the data" | Use `gpt-researcher_quick_search` or `gpt-researcher_deep_research` |
| "Let me delegate to a researcher sub-agent" (when YOU are the researcher) | Do the research yourself with MCP tools |
| Returning 50k tokens of raw context | Synthesize and return 1k-3k token summary |
| Using old URLs from training data | MCP tools do LIVE web searches |