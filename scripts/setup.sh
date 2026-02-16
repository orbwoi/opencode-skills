#!/bin/bash
# OpenCode Skills Setup Script
# Run this on a new machine to configure the development environment
#
# Usage:
#   ./setup.sh [username]
#
# If username not provided, uses current user

set -e

# Get username
if [ -z "$1" ]; then
    USER=$(whoami)
else
    USER=$1
fi

echo "=== OpenCode Development Environment Setup ==="
echo "User: $USER"
echo ""

# Detect OS
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    IS_WINDOWS=true
    GIT_DIR="C:/git"
    VENV_DIR="C:/Users/$USER/.venv"
    SKILLS_DIR="C:/Users/$USER/.agents/skills"
    CONFIG_DIR="C:/Users/$USER/.config/opencode"
else
    IS_WINDOWS=false
    GIT_DIR="$HOME/git"
    VENV_DIR="$HOME/.venv"
    SKILLS_DIR="$HOME/.agents/skills"
    CONFIG_DIR="$HOME/.config/opencode"
fi

# Step 1: Create directories
echo "Step 1: Creating directories..."
mkdir -p "$GIT_DIR"
mkdir -p "$VENV_DIR"
mkdir -p "$SKILLS_DIR"
mkdir -p "$CONFIG_DIR"

# Step 2: Clone repositories
echo "Step 2: Cloning repositories..."
if [ ! -d "$GIT_DIR/opencode-skills" ]; then
    git clone https://github.com/orbwoi/opencode-skills.git "$GIT_DIR/opencode-skills"
fi

if [ ! -d "$GIT_DIR/gpt-researcher" ]; then
    git clone https://github.com/orbwoi/gpt-researcher.git "$GIT_DIR/gpt-researcher"
fi

if [ ! -d "$GIT_DIR/gptr-mcp" ]; then
    git clone https://github.com/orbwoi/gptr-mcp.git "$GIT_DIR/gptr-mcp"
fi

# Step 3: Create virtual environment and install dependencies
echo "Step 3: Setting up Python environment..."
if [ ! -d "$VENV_DIR/gpt-researcher" ]; then
    python -m venv "$VENV_DIR/gpt-researcher"
fi

# Activate venv
if [ "$IS_WINDOWS" = true ]; then
    source "$VENV_DIR/gpt-researcher/Scripts/activate"
else
    source "$VENV_DIR/gpt-researcher/bin/activate"
fi

# Install gpt-researcher from our fork
echo "Installing gpt-researcher..."
cd "$GIT_DIR/gpt-researcher"
pip install -e .

# Install MCP server dependencies
echo "Installing MCP server dependencies..."
cd "$GIT_DIR/gptr-mcp"
pip install -r requirements.txt

# Step 4: Create .env file
echo "Step 4: Creating .env file..."
if [ ! -f "$GIT_DIR/gptr-mcp/.env" ]; then
    cat > "$GIT_DIR/gptr-mcp/.env" << 'EOF'
LLM_PROVIDER=ollama
FAST_LLM=ollama:kimi-k2.5:cloud
SMART_LLM=ollama:kimi-k2.5:cloud
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING=ollama:nomic-embed-text
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
RETRIEVER=duckduckgo
EOF
fi

# Step 5: Configure OpenCode
echo "Step 5: Configuring OpenCode..."
if [ ! -f "$CONFIG_DIR/opencode.json" ]; then
    if [ "$IS_WINDOWS" = true ]; then
        cat > "$CONFIG_DIR/opencode.json" << EOF
{
    "\$schema": "https://opencode.ai/config.json",
    "mcp": {
        "gpt-researcher": {
            "command": [
                "C:/Users/$USER/.venv/gpt-researcher/Scripts/python.exe",
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
EOF
    else
        cat > "$CONFIG_DIR/opencode.json" << EOF
{
    "\$schema": "https://opencode.ai/config.json",
    "mcp": {
        "gpt-researcher": {
            "command": [
                "$HOME/.venv/gpt-researcher/bin/python",
                "$HOME/git/gptr-mcp/server.py"
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
EOF
    fi
fi

# Step 6: Install skills
echo "Step 6: Installing skills..."
cp -r "$GIT_DIR/opencode-skills/skills/"* "$SKILLS_DIR/"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "What was installed:"
echo "  - Repositories: $GIT_DIR/opencode-skills, $GIT_DIR/gpt-researcher, $GIT_DIR/gptr-mcp"
echo "  - Python venv: $VENV_DIR/gpt-researcher"
echo "  - Skills: $SKILLS_DIR"
echo "  - Config: $CONFIG_DIR/opencode.json"
echo ""
echo "Next steps:"
echo "  1. Make sure Ollama is running on localhost:11434"
echo "  2. Pull required models: ollama pull kimi-k2.5:cloud, ollama pull nomic-embed-text"
echo "  3. Restart OpenCode to load new MCP tools and skills"
echo ""
echo "To verify: Run 'opencode' and check that gpt-researcher tools are available"