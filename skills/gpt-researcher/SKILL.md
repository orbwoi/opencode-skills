---
name: gpt-researcher
description: Research skill for AI agents. Use this skill when you need to conduct web searches or deep research. Provides access to MCP tools for quick searches and deep research with automatic HTML-to-Markdown conversion. All outputs are clean Markdown-formatted text suitable for LLM consumption.
---

# GPT Researcher Agent Skill

This skill provides instructions for using research MCP tools to gather information from the web with clean Markdown output.

## Output Format

**ALL research output is Markdown only.** HTML tags and entities are automatically stripped from:
- Search result snippets
- Research context
- Scraped web content

This ensures clean, token-efficient output suitable for LLM context.

---

## When to Use Research Tools

| Need | Tool | Approach |
|------|------|----------|
| Quick fact/lookup | `quick_search` | **Direct tool call** |
| ANY research | `deep_research` | **Sub-agent delegation** |
| Report from research | `write_report` | Direct tool call (uses research_id) |

### Decision Flow

```
Is this a simple lookup (single fact, definition, current value)?
  → YES: Call quick_search directly
  → NO: Delegate to researcher sub-agent

NEVER call deep_research directly - always use sub-agent to protect context.
```

### Why Always Use Sub-Agent for Research

**Direct `deep_research` call:**
- Returns 10k-50k+ tokens of raw context
- Pollutes your context window
- Wastes tokens on scraped web content

**Sub-agent delegation:**
- Returns synthesized summary (1k-3k tokens)
- Raw context stays in sub-agent
- Main context stays clean
- Sub-agent can iterate and refine

**Exception:** Only call `deep_research` directly if you explicitly need the raw research context for further processing in your session.

---

## Quick Search

**ALWAYS call directly** - lightweight, minimal context impact.

Use for: Single facts, definitions, current prices, simple lookups

```python
# Direct tool call - fast and lightweight
result = gpt_researcher_quick_search(query="current Bitcoin price")
```

**Returns:**
- `search_results`: List of {title, href, body} - HTML cleaned
- `result_count`: Number of results

**Best practices:**
- Specific queries get better results
- Use for time-sensitive information
- Perfect for verifying facts or getting snippets

---

## Deep Research

**ALWAYS delegate to sub-agent** - protects your context window.

Use for: ANY topic requiring more than a simple lookup

### Sub-Agent Delegation (DEFAULT)

```
Task tool with subagent_type: "researcher"
```

The sub-agent:
1. Calls deep_research internally
2. Processes and synthesizes findings 
3. Returns final markdown report
4. Main agent context stays clean (~1-3k tokens vs 50k+ raw)

**Example prompt for sub-agent:**
```
Research GLM-5 hosting providers in the USA.
Focus on: pricing, privacy compliance, and context window support.
Return a comparison table with your top 5 recommendations.
```

### Direct Tool Call (EXCEPTION - use sparingly)

Only call `gpt_researcher_deep_research` directly when:
- You need raw context for further processing
- You plan to use `write_report` in the same session
- You explicitly want the full scraped content

```python
# Direct call - only for special cases
result = gpt_researcher_deep_research(
    query="Compare GLM-5 providers in USA with privacy compliance"
)
# result["context"] contains 10k-50k+ tokens of raw content
```

---

## Writing Reports

After deep research, generate a structured report:

```python
# First conduct research
research = gpt_researcher_deep_research(query="...")

# Then write report using the research_id
report = gpt_researcher_write_report(
    research_id=research["research_id"],
    custom_prompt="Focus on pricing and privacy features"
)
```

**Report is always Markdown formatted.**

---

## Research Best Practices

### Query Formulation

| Good Query | Bad Query |
|------------|-----------|
| "GLM-5 hosting providers USA with zero data retention" | "tell me about AI" |
| "Cloudflare Markdown for Agents feature February 2026" | "what's new" |
| "compare DeepInfra vs Fireworks pricing for GLM-5" | "cheap AI" |

### Context Management

1. **Quick lookups** → Call `quick_search` directly
2. **Any research** → Delegate to `Task(subagent_type="researcher")`
3. **Need raw context?** → Call `deep_research` directly (exception)
4. **Reports** → Use `write_report` after direct `deep_research`

### Token Comparison

| Approach | Context Impact | When to Use |
|----------|----------------|-------------|
| `quick_search` direct | ~500 tokens | Simple facts |
| `deep_research` direct | 10k-50k tokens | Need raw context |
| Sub-agent + researcher | 1k-3k tokens | Default for all research |

### Multi-Step Research

For complex research requiring multiple angles:

1. Start with `quick_search` for overview
2. Use `deep_research` for detailed analysis
3. Call `write_report` for final synthesis
4. Use `get_research_sources` for citations if needed

---

## Available Tools

| Tool | Purpose | Output |
|------|---------|--------|
| `gpt_researcher_quick_search` | Fast web search | Cleaned search snippets |
| `gpt_researcher_deep_research` | Comprehensive research | Cleaned context + research_id |
| `gpt_researcher_write_report` | Generate report | Markdown report |
| `gpt_researcher_get_research_sources` | Get source URLs | URL list |
| `gpt_researcher_get_research_context` | Retrieve stored context | Cleaned context |

---

## Privacy & Data Handling

When researching privacy-sensitive topics, ask for:
- Zero Data Retention (ZDR) policies
- No-training-on-user-data policies  
- Data residency requirements
- Compliance certifications (SOC 2, ISO 27001, HIPAA)

---

## Example Usage Session

```
User: "Find the best GLM-5 providers in USA with zero data retention"

Agent:
1. quick_search("GLM-5 providers USA zero data retention")
   → Gets quick overview of providers
   
2. Task(subagent_type="researcher", prompt="Research GLM-5 hosting providers in USA.
   Compare pricing, privacy compliance (ZDR, no-training), and features.
   Return top 5 recommendations in a comparison table.")
   → Sub-agent handles all research internally
   → Returns clean summary (not 50k tokens of raw context)
```

## Red Flags

| ❌ Don't Do This | ✅ Do This Instead |
|------------------|-------------------|
| Call `deep_research` directly for general research | Delegate to researcher sub-agent |
| Accept 50k tokens of raw scraped content | Get 1-3k token synthesized summary |
| Wonder why your context is full | Use sub-agent isolation |