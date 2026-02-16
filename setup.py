#!/usr/bin/env python3
"""
OpenCode Skills Setup Script
Cross-platform setup for development environment

Works on: Windows, Linux, macOS
Requires: Python 3.8+, Git

Usage:
    python setup.py              # Interactive setup
    python setup.py --user john  # Specify username (Windows)
    python setup.py --dry-run    # Preview actions
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_step(step: str, message: str):
    print(f"{Colors.OKCYAN}[{step}]{Colors.ENDC} {message}")


def print_success(message: str):
    print(f"{Colors.OKGREEN}✓{Colors.ENDC} {message}")


def print_warning(message: str):
    print(f"{Colors.WARNING}!{Colors.ENDC} {message}")


def print_error(message: str):
    print(f"{Colors.FAIL}✗{Colors.ENDC} {message}")


def run_cmd(cmd: list, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a command, handling platform differences."""
    result = subprocess.run(cmd, capture_output=capture, text=True)
    if check and result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)
    return result


def is_windows() -> bool:
    return platform.system() == "Windows"


def is_macos() -> bool:
    return platform.system() == "Darwin"


def is_linux() -> bool:
    return platform.system() == "Linux"


class SetupConfig:
    def __init__(self, user: Optional[str] = None, dry_run: bool = False):
        self.dry_run = dry_run
        self.home = Path.home()
        
        if user and is_windows():
            self.home = Path(f"C:/Users/{user}")
        
        # Platform-specific paths
        if is_windows():
            self.git_dir = Path("C:/git")
            self.venv_dir = self.home / ".venv"
            self.skills_dir = self.home / ".agents" / "skills"
            self.config_dir = self.home / ".config" / "opencode"
            self.npm_global = self.home / "AppData" / "Roaming" / "npm"
        else:
            self.git_dir = self.home / "git"
            self.venv_dir = self.home / ".venv"
            self.skills_dir = self.home / ".agents" / "skills"
            self.config_dir = self.home / ".config" / "opencode"
            self.npm_global = self.home / ".npm-global"

    def get_python_exe(self) -> Path:
        """Get the Python executable path for the gpt-researcher venv."""
        if is_windows():
            return self.venv_dir / "gpt-researcher" / "Scripts" / "python.exe"
        return self.venv_dir / "gpt-researcher" / "bin" / "python"

    def get_opencode_config(self) -> dict:
        """Generate opencode.json configuration."""
        python_exe = str(self.get_python_exe()).replace("\\", "/")
        mcp_path = str(self.git_dir / "gptr-mcp" / "server.py").replace("\\", "/")
        
        return {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {
                "gpt-researcher": {
                    "command": [python_exe, mcp_path],
                    "enabled": True,
                    "environment": {
                        "EMBEDDING": "ollama:nomic-embed-text",
                        "FAST_LLM": "ollama:kimi-k2.5:cloud",
                        "LLM_PROVIDER": "ollama",
                        "OLLAMA_BASE_URL": "http://localhost:11434",
                        "OLLAMA_EMBEDDING_MODEL": "nomic-embed-text",
                        "RETRIEVER": "duckduckgo",
                        "SMART_LLM": "ollama:kimi-k2.5:cloud"
                    },
                    "type": "local",
                    "timeout": 300000
                }
            }
        }


class OpenCodeSetup:
    def __init__(self, config: SetupConfig):
        self.config = config
        self.steps = [
            ("Checking prerequisites", self.check_prerequisites),
            ("Creating directories", self.create_directories),
            ("Cloning repositories", self.clone_repos),
            ("Setting up Python environment", self.setup_python),
            ("Installing agent-browser", self.install_agent_browser),
            ("Installing skills CLI", self.install_skills_cli),
            ("Installing agent-browser skill", self.install_agent_browser_skill),
            ("Configuring OpenCode", self.configure_opencode),
            ("Installing gpt-researcher skill", self.install_gpt_researcher_skill),
        ]

    def run(self):
        print(f"\n{Colors.HEADER}=== OpenCode Development Environment Setup ==={Colors.ENDC}\n")
        print(f"Platform: {platform.system()}")
        print(f"Home: {self.config.home}")
        print(f"Git directory: {self.config.git_dir}")
        print()

        if self.config.dry_run:
            print(f"{Colors.WARNING}DRY RUN - no changes will be made{Colors.ENDC}\n")

        for step_name, step_func in self.steps:
            print_step("STEP", step_name)
            try:
                if self.config.dry_run:
                    print("  (skipped - dry run)")
                else:
                    step_func()
                print()
            except Exception as e:
                print_error(f"Failed: {e}")
                if not self.config.dry_run:
                    sys.exit(1)

        self.print_summary()

    def check_prerequisites(self):
        # Check Python
        python_version = sys.version_info
        if python_version < (3, 8):
            raise RuntimeError(f"Python 3.8+ required, found {python_version.major}.{python_version.minor}")
        print_success(f"Python {python_version.major}.{python_version.minor}.{python_version.micro}")

        # Check Git
        result = run_cmd(["git", "--version"], capture=True)
        print_success(f"Git installed")

        # Check Node.js (optional, warn if missing)
        result = run_cmd(["node", "--version"], check=False, capture=True)
        if result.returncode == 0:
            print_success(f"Node.js {result.stdout.strip()}")
        else:
            print_warning("Node.js not found - required for agent-browser and skills CLI")
            print_warning("Install from: https://nodejs.org/")

        # Check npm
        result = run_cmd(["npm", "--version"], check=False, capture=True)
        if result.returncode == 0:
            print_success(f"npm {result.stdout.strip()}")

    def create_directories(self):
        dirs = [
            self.config.git_dir,
            self.config.venv_dir,
            self.config.skills_dir,
            self.config.config_dir,
        ]
        
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            print_success(f"Created {d}")

    def clone_repos(self):
        repos = [
            ("https://github.com/orbwoi/opencode-skills.git", "opencode-skills"),
            ("https://github.com/orbwoi/gpt-researcher.git", "gpt-researcher"),
            ("https://github.com/orbwoi/gptr-mcp.git", "gptr-mcp"),
        ]
        
        for url, name in repos:
            repo_path = self.config.git_dir / name
            if repo_path.exists():
                print_success(f"{name} already exists, skipping clone")
            else:
                run_cmd(["git", "clone", url, str(repo_path)])
                print_success(f"Cloned {name}")

    def setup_python(self):
        venv_path = self.config.venv_dir / "gpt-researcher"
        
        if venv_path.exists():
            print_success(f"Virtual environment already exists at {venv_path}")
        else:
            run_cmd([sys.executable, "-m", "venv", str(venv_path)])
            print_success(f"Created virtual environment at {venv_path}")

        # Get venv python
        venv_python = self.config.get_python_exe()
        
        # Upgrade pip
        run_cmd([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], capture=True)
        print_success("Upgraded pip")

        # Install gpt-researcher from our fork
        gpt_researcher_path = self.config.git_dir / "gpt-researcher"
        run_cmd([str(venv_python), "-m", "pip", "install", "-e", str(gpt_researcher_path)], capture=True)
        print_success("Installed gpt-researcher (editable)")

        # Install MCP server dependencies
        mcp_path = self.config.git_dir / "gptr-mcp"
        requirements = mcp_path / "requirements.txt"
        if requirements.exists():
            run_cmd([str(venv_python), "-m", "pip", "install", "-r", str(requirements)], capture=True)
            print_success("Installed MCP server dependencies")

        # Create .env file
        env_file = mcp_path / ".env"
        if not env_file.exists():
            env_content = """LLM_PROVIDER=ollama
FAST_LLM=ollama:kimi-k2.5:cloud
SMART_LLM=ollama:kimi-k2.5:cloud
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING=ollama:nomic-embed-text
OLLAMA_EMBEDDING_MODEL=nomic-embed-text
RETRIEVER=duckduckgo
"""
            env_file.write_text(env_content)
            print_success(f"Created {env_file}")
        else:
            print_success(f".env already exists at {env_file}")

    def install_agent_browser(self):
        """Install agent-browser CLI tool globally via npm."""
        result = run_cmd(["npm", "install", "-g", "agent-browser"], check=False, capture=True)
        if result.returncode == 0:
            print_success("Installed agent-browser globally")
            
            # Install Chromium for agent-browser
            run_cmd(["agent-browser", "install"], check=False, capture=True)
            print_success("Downloaded Chromium for agent-browser")
        else:
            print_warning("Failed to install agent-browser (npm install may need admin)")
            print_warning("Try manually: npm install -g agent-browser")

    def install_skills_cli(self):
        """Install skills CLI - no installation needed, uses npx."""
        # Verify npx works
        result = run_cmd(["npx", "skills", "--help"], check=False, capture=True)
        if result.returncode == 0:
            print_success("Skills CLI available via npx")
        else:
            print_warning("Skills CLI not available - check npm/npx installation")

    def install_agent_browser_skill(self):
        """Install agent-browser skill from skills.sh using the skills CLI."""
        result = run_cmd(
            ["npx", "skills", "add", "vercel-labs/agent-browser", "-g", "-y"],
            check=False,
            capture=True
        )
        if result.returncode == 0:
            print_success("Installed agent-browser skill")
        else:
            print_warning("Failed to install agent-browser skill")
            print_warning("Try manually: npx skills add vercel-labs/agent-browser -g")

    def configure_opencode(self):
        """Create opencode.json configuration."""
        config_file = self.config.config_dir / "opencode.json"
        
        if config_file.exists():
            print_warning(f"{config_file} already exists, backing up")
            backup = config_file.with_suffix(".json.backup")
            shutil.copy(config_file, backup)
            print_success(f"Backup created at {backup}")

        config_data = self.config.get_opencode_config()
        config_file.write_text(json.dumps(config_data, indent=4))
        print_success(f"Created {config_file}")

    def install_gpt_researcher_skill(self):
        """Install gpt-researcher skill from local repo."""
        skill_source = self.config.git_dir / "opencode-skills" / "skills" / "gpt-researcher"
        skill_dest = self.config.skills_dir / "gpt-researcher"
        
        if skill_source.exists():
            if skill_dest.exists():
                shutil.rmtree(skill_dest)
            shutil.copytree(skill_source, skill_dest)
            print_success(f"Installed gpt-researcher skill to {skill_dest}")
        else:
            print_warning(f"Skill source not found at {skill_source}")

    def print_summary(self):
        print(f"\n{Colors.HEADER}=== Setup Complete ==={Colors.ENDC}\n")
        print("Installed components:")
        print(f"  • Repositories: {self.config.git_dir}")
        print(f"  • Python venv:  {self.config.venv_dir / 'gpt-researcher'}")
        print(f"  • Skills:       {self.config.skills_dir}")
        print(f"  • Config:       {self.config.config_dir / 'opencode.json'}")
        print()
        print("Installed tools:")
        print("  • agent-browser (npm global)")
        print("  • skills CLI (via npx)")
        print()
        print("Installed skills:")
        print("  • agent-browser (from skills.sh)")
        print("  • gpt-researcher (from local repo)")
        print()
        print(f"{Colors.BOLD}Next steps:{Colors.ENDC}")
        print("  1. Ensure Ollama is running on localhost:11434")
        print("  2. Pull required models:")
        print("     ollama pull kimi-k2.5:cloud")
        print("     ollama pull nomic-embed-text")
        print("  3. Restart OpenCode to load new MCP tools and skills")
        print()
        print("To verify:")
        print("  • agent-browser --help")
        print("  • npx skills list")
        print("  • opencode --help")


def main():
    parser = argparse.ArgumentParser(
        description="OpenCode Skills Setup Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python setup.py              # Interactive setup
    python setup.py --user john  # Specify Windows username
    python setup.py --dry-run    # Preview actions without making changes
        """
    )
    parser.add_argument("--user", help="Username (Windows only)")
    parser.add_argument("--dry-run", action="store_true", help="Preview actions without making changes")
    
    args = parser.parse_args()
    
    config = SetupConfig(user=args.user, dry_run=args.dry_run)
    setup = OpenCodeSetup(config)
    setup.run()


if __name__ == "__main__":
    main()