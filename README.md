# OpenCode Skills & Configuration

Agent skills and setup configuration for OpenCode development environment.

## Quick Start

On a new machine, point an agent at this README:

```
https://github.com/orbwoi/opencode-skills
```

Then ask it to run the setup:

```
Follow the setup instructions in the README to configure this machine for opencode development
```

## What This Configures

| Component | Purpose | Location |
|-----------|---------|----------|
| **Skills** | Agent instructions for specialized tasks | `~/.agents/skills/` |
| **MCP Server** | GPT Researcher with Ollama support | `C:\git\gptr-mcp\` |
| **GPT Researcher** | Web research library (modified) | `C:\git\gpt-researcher\` |
| **OpenCode Config** | MCP and tool configuration | `~/.config/opencode/opencode.json` |

## Setup Instructions

### Prerequisites

- Python 3.10+ 
- Git
- Ollama running on `localhost:11434`
- OpenCode CLI installed

### Step 1: Clone Repositories

```bash
# Create git directory
mkdir -p C:\git

# Clone our forks (these include our modifications)
git clone https://github.com/orbwoi/opencode-skills.git C:\git\opencode-skills
git clone https://github.com/orbwoi/gpt-researcher.git C:\git\gpt-researcher
git clone https://github.com/orbwoi/gptr-mcp.git C:\git\gptr-mcp
```

### Step 2: Install GPT Researcher

```bash
# Create virtual environment
python -m venv C:\Users\<user>\.venv\gpt-researcher
C:\Users\<user>\.venv\gpt-researcher\Scripts\activate

# Install gpt-researcher from our fork (editable mode)
cd C:\git\gpt-researcher
pip install -e .

# Install MCP server dependencies
cd C:\git\gptr-mcp
pip install -r requirements.txt
```

### Step 3: Configure MCP Server

Create `.env` in `C:\git\gptr-mcp\`:

```env
LLM_PROVIDER=ollama
FAST_LLM=ollama:kimi-k2.5:cloud
SMART_LLM=ollama:kimi-k2.5:cloud
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING=ollama:nomic-embed-text
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
RETRIEVER=duckduckgo
```

### Step 4: Configure OpenCode

Create or update `~/.config/opencode/opencode.json`:

```json
{
    "$schema": "https://opencode.ai/config.json",
    "mcp": {
        "gpt-researcher": {
            "command": [
                "C:/Users/<user>/.venv/gpt-researcher/Scripts/python.exe",
                "C:/git/gptr-mcp/server.py"
            ],
            "enabled": true,
            "environment": {
                "EMBEDDING": "ollama:nomic-embed-text",
                "FAST_LLM": "ollama:kimi-k2.5:cloud",
                "LLM_PROVIDER": "ollama",
                "OLLAMA_BASE_URL": "http://localhost:11434",
                "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
                "RETRIEVER": "duckduckgo",
                "SMART_LLM": "ollama:kimi-k2.5:cloud"
            },
            "type": "local"
        }
    }
}
```

### Step 5: Install Skills

```bash
# Create skills directory
mkdir -p C:\Users\<user>\.agents\skills

# Copy skills from repo
cp -r C:\git\opencode-skills\skills\* C:\Users\<user>\.agents\skills\
```

### Step 6: Verify Setup

```bash
# Test MCP server
cd C:\git\gptr-mcp
C:\Users\<user>\.venv\gpt-researcher\Scripts\python.exe server.py

# In another terminal, test OpenCode
opencode --help
```

## Skills Included

### gpt-researcher

Instructions for using research MCP tools.

**When to use:**
- Quick fact lookups → `gpt-researcher_quick_search`
- Comprehensive research → `gpt-researcher_deep_research` via Task tool
- Report generation → `gpt-researcher_write_report`

**Output:** All Markdown, HTML stripped automatically.

## Our Fork Modifications

### gpt-researcher Fork

**URL:** https://github.com/orbwoi/gpt-researcher

**Modifications:**
- Added Cloudflare Markdown for Agents support (`Accept: text/markdown` header)
- HTTP scrapers request markdown before falling back to HTML
- Reduces token usage ~80% on Cloudflare Pro sites

**Files changed:**
- `gpt_researcher/scraper/beautiful_soup/beautiful_soup.py`
- `gpt_researcher/scraper/web_base_loader/web_base_loader.py`
- `gpt_researcher/scraper/utils.py`

**Upstream:** https://github.com/assafelovic/gpt-researcher

### gptr-mcp Fork

**URL:** https://github.com/orbwoi/gptr-mcp

**Modifications:**
- Added HTML stripping for clean Markdown output
- `strip_html()` decodes entities and removes tags
- `clean_search_results()` for DuckDuckGo snippets
- `clean_context()` for research context
- All tools return Markdown-safe content

**Files changed:**
- `server.py`
- `utils.py`

**Upstream:** https://github.com/assafelovic/gptr-mcp

## Syncing with Upstream

To pull latest changes from upstream:

```bash
# gpt-researcher
cd C:\git\gpt-researcher
git fetch upstream
git merge upstream/main

# gptr-mcp
cd C:\git\gptr-mcp
git fetch upstream
git merge upstream/master
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CODING AGENT                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Quick lookup (fast)          Deep research (autonomous)    │
│  ─────────────────────        ──────────────────────────    │
│  quick_search() directly      → Task(subagent: researcher)  │
│  (minimal context)               → calls MCP tools          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      MCP TOOLS                               │
│  quick_search, deep_research, write_report, get_sources     │
│  → All output: Clean Markdown (HTML stripped)               │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  GPT RESEARCHER LIBRARY                      │
│  Scrapers with Cloudflare Markdown support                  │
│  Accept: text/markdown → ~80% token reduction               │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### MCP server not starting
- Check Python venv path in opencode.json
- Verify `.env` exists in `C:\git\gptr-mcp\`
- Ensure Ollama is running

### Skills not loading
- Verify skills are in `~/.agents/skills\`
- Check SKILL.md has correct YAML frontmatter

### HTML still appearing in output
- MCP server should strip HTML automatically
- File an issue if raw HTML persists

## License

Individual components maintain their original licenses:
- GPT Researcher: MIT
- gptr-mcp: MIT