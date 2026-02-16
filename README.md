# OpenCode Skills & Configuration

Agent skills and setup configuration for OpenCode development environment.

## Quick Start

On a new machine, run:

```bash
# Clone and run setup
git clone https://github.com/orbwoi/opencode-skills.git
cd opencode-skills
python setup.py
```

That's it! The setup script handles everything.

## What Gets Installed

| Component | Purpose | Location |
|-----------|---------|----------|
| **agent-browser** | Browser automation CLI | npm global |
| **skills CLI** | Skill package manager | via npx |
| **agent-browser skill** | Browser automation instructions | `~/.agents/skills/` |
| **gpt-researcher** | Web research library (modified) | `~/git/gpt-researcher/` |
| **gptr-mcp** | MCP server for research | `~/git/gptr-mcp/` |
| **gpt-researcher skill** | Research tool instructions | `~/.agents/skills/` |
| **OpenCode config** | MCP configuration | `~/.config/opencode/opencode.json` |

## Prerequisites

Before running setup, ensure you have:

| Requirement | How to Install |
|-------------|----------------|
| **Python 3.8+** | [python.org](https://python.org) |
| **Git** | [git-scm.com](https://git-scm.com) |
| **Node.js 18+** | [nodejs.org](https://nodejs.org) |
| **Ollama** | [ollama.ai](https://ollama.ai) |

## Setup Options

```bash
# Standard setup
python setup.py

# Windows with specific user
python setup.py --user john

# Preview without making changes
python setup.py --dry-run
```

## After Setup

1. **Start Ollama** (if not running):
   ```bash
   ollama serve
   ```

2. **Pull required models**:
   ```bash
   ollama pull kimi-k2.5:cloud
   ollama pull nomic-embed-text
   ```

3. **Restart OpenCode** to load new tools and skills

## Verify Installation

```bash
# Check agent-browser
agent-browser --help

# Check skills CLI
npx skills list

# Test MCP server
python ~/git/gptr-mcp/server.py
```

## Installed Tools

### agent-browser (Vercel Labs)

Headless browser automation CLI optimized for AI agents.

**Key features:**
- Ref-based element selection (deterministic)
- Accessibility tree snapshots
- Session persistence
- Cross-platform (Windows, Linux, macOS)

**Quick example:**
```bash
agent-browser open example.com
agent-browser snapshot -i        # Get interactive elements
agent-browser click @e1          # Click by ref
agent-browser fill @e2 "text"    # Fill by ref
agent-browser screenshot out.png
agent-browser close
```

**Full docs:** `agent-browser --help` or [npmjs.com/package/agent-browser](https://npmjs.com/package/agent-browser)

### skills CLI (skills.sh)

Package manager for AI agent skills.

**Key commands:**
```bash
npx skills find <query>          # Search for skills
npx skills add <owner/repo> -g   # Install skill globally
npx skills list                  # List installed skills
npx skills check                 # Check for updates
npx skills update                # Update all skills
```

**Browse skills:** [skills.sh](https://skills.sh)

### gpt-researcher MCP Server

Provides deep web research capabilities.

**Tools:**
- `gpt-researcher_quick_search` - Fast web search
- `gpt-researcher_deep_research` - Comprehensive research
- `gpt-researcher_write_report` - Generate markdown reports

**Output:** All Markdown, HTML stripped automatically.

## Our Fork Modifications

### gpt-researcher Fork

**URL:** https://github.com/orbwoi/gpt-researcher

**Modifications:**
- Cloudflare Markdown for Agents support (`Accept: text/markdown`)
- ~80% token reduction on Cloudflare Pro sites
- Falls back to HTML parsing automatically

**Upstream:** https://github.com/assafelovic/gpt-researcher

### gptr-mcp Fork

**URL:** https://github.com/orbwoi/gptr-mcp

**Modifications:**
- HTML stripping for clean Markdown output
- `strip_html()`, `clean_search_results()`, `clean_context()`
- All tools return Markdown-safe content

**Upstream:** https://github.com/assafelovic/gptr-mcp

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      CODING AGENT                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Skills loaded from ~/.agents/skills/                       │
│  • agent-browser (browser automation)                       │
│  • gpt-researcher (web research)                            │
│                                                             │
│  MCP Tools available:                                       │
│  • gpt-researcher_quick_search                              │
│  • gpt-researcher_deep_research                             │
│  • gpt-researcher_write_report                              │
│                                                             │
│  CLI Tools available:                                       │
│  • agent-browser (browser automation)                       │
│  • npx skills (skill package manager)                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Manual Setup (Alternative)

If you prefer manual setup:

### Step 1: Install Tools

```bash
# Install agent-browser
npm install -g agent-browser
agent-browser install  # Download Chromium

# Skills CLI works via npx (no install needed)
npx skills --help
```

### Step 2: Install Skills

```bash
# Install agent-browser skill from skills.sh
npx skills add vercel-labs/agent-browser -g

# Clone our skills repo for gpt-researcher
git clone https://github.com/orbwoi/opencode-skills.git
cp -r opencode-skills/skills/* ~/.agents/skills/
```

### Step 3: Clone Research Tools (Optional)

```bash
git clone https://github.com/orbwoi/gpt-researcher.git
git clone https://github.com/orbwoi/gptr-mcp.git

# Setup Python
python -m venv ~/.venv/gpt-researcher
source ~/.venv/gpt-researcher/bin/activate  # Linux/Mac
# or: ~/.venv/gpt-researcher/Scripts/activate  # Windows

pip install -e ./gpt-researcher
pip install -r ./gptr-mcp/requirements.txt
```

### Step 4: Configure OpenCode

Create `~/.config/opencode/opencode.json` with the MCP server config (see `setup.py` for template).

## Syncing with Upstream

To pull latest changes:

```bash
cd ~/git/gpt-researcher && git fetch upstream && git merge upstream/main
cd ~/git/gptr-mcp && git fetch upstream && git merge upstream/master
```

## Troubleshooting

### npm permission errors (Linux/macOS)
```bash
mkdir -p ~/.npm-global
npm config set prefix ~/.npm-global
# Add to ~/.bashrc: export PATH=~/.npm-global/bin:$PATH
```

### Windows: agent-browser not found
Ensure npm global bin is in PATH:
```
%APPDATA%\npm
```

### MCP server not starting
- Check Python venv path in opencode.json
- Verify `.env` exists in `~/git/gptr-mcp/`
- Ensure Ollama is running on localhost:11434

## License

Individual components maintain their original licenses:
- agent-browser: Apache-2.0
- GPT Researcher: MIT
- gptr-mcp: MIT