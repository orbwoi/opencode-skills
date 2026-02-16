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

| Need | Tool | Speed | Context Impact |
|------|------|-------|----------------|
| Quick fact/lookup | `gpt-researcher_quick_search` | ~3-5 seconds | Minimal - call directly |
| Comprehensive research | `gpt-researcher_deep_research` | ~1-3 minutes | Isolated - delegate to sub-agent |
| Full report | `gpt-researcher_write_report` | ~30 seconds | Uses existing research_id |

### Decision Flow

```
Is this a simple lookup (single fact, definition, current value)?
  → YES: Use quick_search directly (fast, minimal context)
  → NO: Is this a complex topic requiring multiple sources?
         → YES: Delegate to researcher sub-agent (context isolated)
         → NO: Use quick_search with 5-10 results
```

---

## Quick Search

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

Use for: Comprehensive topics, multi-faceted questions, technical deep-dives

### Option 1: Direct Tool Call (adds context to current session)

```python
result = gpt_researcher_deep_research(
    query="Compare GLM-5 providers in USA with privacy compliance"
)
# Use result["context"] directly - cleaned of HTML
```

### Option 2: Sub-Agent Delegation (isolated context)

Use when:
- Research will generate large context
- You want to protect main context window
- Research is autonomous and comprehensive

```
Task tool with subagent_type: "researcher"
```

The sub-agent:
1. Calls deep_research internally
2. Processes and synthesizes findings 
3. Returns final markdown report
4. Main agent context stays clean

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
2. **Medium research** → Call `deep_research` directly, use returned context
3. **Large research** → Delegate to `Task(subagent_type="researcher")`
4. **Reports** → Use `write_report` after deep_research

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
   → Gets overview of providers
   
2. deep_research("GLM-5 hosting providers USA comparison privacy compliance pricing")
   → Detailed research with sources
   
3. write_report(research_id, "Compare pricing, privacy, and performance")
   → Structured markdown report
```