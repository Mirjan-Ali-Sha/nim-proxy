import os
import sys
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from .config import settings, save_config

console = Console()

def show_welcome():
    welcome_text = """
    🚀 NVIDIA NIM Proxy for Claude Code
    [dim]Created By: Mirjan Ali Sha[/dim]
    
    Translate Anthropic API calls to NVIDIA NIM instantly.
    """
    console.print(Panel(welcome_text, title="[bold green]NIM Proxy[/bold green]", expand=False))

def setup_env_help():
    powershell_cmd = '$env:ANTHROPIC_AUTH_TOKEN="nim-proxy"; $env:ANTHROPIC_API_KEY="sk-ant-dummy"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; claude'
    bash_cmd = 'export ANTHROPIC_AUTH_TOKEN="nim-proxy"; export ANTHROPIC_API_KEY="sk-ant-dummy"; export ANTHROPIC_BASE_URL="http://localhost:8082"; claude'
    
    console.print("\n[bold cyan]How to connect Claude Code to this Proxy:[/bold cyan]")
    
    console.print("\n[bold]Step 0: Install Claude Code (if needed)[/bold]")
    console.print(Syntax("npm install -g @anthropic-ai/claude-code", "bash"))

    console.print("\n[bold]Step 1: Connect to Proxy (One-off)[/bold]")
    console.print("[yellow]PowerShell (Windows):[/yellow]")
    console.print(Syntax(powershell_cmd, "powershell"))
    console.print("[yellow]Bash/Zsh (Linux/macOS):[/yellow]")
    console.print(Syntax(bash_cmd, "bash"))

    console.print("\n[bold]Option 2: Permanently (Sticky)[/bold]")
    console.print("[yellow]Windows PowerShell Profile:[/yellow]")
    console.print(f"Add this to {os.path.expanduser('~')}\\Documents\\PowerShell\\Microsoft.PowerShell_profile.ps1:")
    console.print(Syntax('$env:ANTHROPIC_AUTH_TOKEN="nim-proxy"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; $env:ANTHROPIC_API_KEY="sk-ant-dummy"', "powershell"))
    
    console.print("[yellow]Linux/macOS (~/.bashrc or ~/.zshrc):[/yellow]")
    console.print(Syntax('export ANTHROPIC_AUTH_TOKEN="nim-proxy"; export ANTHROPIC_BASE_URL="http://localhost:8082"; export ANTHROPIC_API_KEY="sk-ant-dummy"', "bash"))

def main():
    parser = argparse.ArgumentParser(description="NVIDIA NIM Proxy for Claude Code")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Start command
    start_parser = subparsers.add_parser("start", help="Launch the proxy server (Drop-in Anthropic API)")
    start_parser.add_argument("--port", type=int, default=8082, help="Port to run on (default: 8082)")
    start_parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (use 127.0.0.1 for local only)")

    # Config command
    config_parser = subparsers.add_parser("config", help="Update proxy settings (API keys, model mappings, and generation defaults)")
    config_parser.add_argument("--key", type=str, help="Your NVIDIA NIM API Key (starts with nvapi-)")
    config_parser.add_argument("--opus", type=str, help="NIM Model ID to use for Claude Opus requests")
    config_parser.add_argument("--sonnet", type=str, help="NIM Model ID to use for Claude Sonnet requests")
    config_parser.add_argument("--haiku", type=str, help="NIM Model ID to use for Claude Haiku requests")
    config_parser.add_argument("--fallback", type=str, help="NIM Model ID used when primary models fail")
    
    # Param flags
    config_parser.add_argument("--temp", type=float, help="Default temperature for generation (0.0 to 1.0)")
    config_parser.add_argument("--max-tokens", type=int, help="Default maximum tokens to generate per response")
    config_parser.add_argument("--reasoning", type=str, choices=["low", "medium", "high"], help="Default reasoning effort for 'Thinking' models")
    config_parser.add_argument("--thinking", type=str, choices=["true", "false"], help="Enable or disable native reasoning/thinking blocks")
    config_parser.add_argument("--optimize", type=str, choices=["true", "false"], help="Enable fast-path optimizations for common tool probes")

    # Help command
    subparsers.add_parser("setup-env", help="Show the setup commands for Windows (PowerShell) and Linux/macOS (Zsh/Bash)")

    args = parser.parse_args()

    if args.command == "start":
        import uvicorn
        from .server import app
        show_welcome()
        console.print(f"Starting server on {args.host}:{args.port}...")
        uvicorn.run(app, host=args.host, port=args.port)

    elif args.command == "config":
        if args.key: settings.NVIDIA_NIM_API_KEY = args.key
        if args.opus: settings.MODEL_OPUS = args.opus
        if args.sonnet: settings.MODEL_SONNET = args.sonnet
        if args.haiku: settings.MODEL_HAIKU = args.haiku
        if args.fallback: settings.MODEL_FALLBACK = args.fallback
        
        if args.temp is not None: settings.DEFAULT_TEMPERATURE = args.temp
        if args.max_tokens is not None: settings.DEFAULT_MAX_TOKENS = args.max_tokens
        if args.reasoning: settings.DEFAULT_REASONING_EFFORT = args.reasoning
        if args.thinking: settings.ENABLE_THINKING = args.thinking == "true"
        if args.optimize: settings.ENABLE_OPTIMIZATIONS = args.optimize == "true"
        
        save_config()
        console.print("[bold green]Configuration updated successfully![/bold green]")
        console.print(f"API Key: {'*' * 10}{settings.NVIDIA_NIM_API_KEY[-4:] if settings.NVIDIA_NIM_API_KEY else 'Not Set'}")
        console.print(f"Opus Model: {settings.MODEL_OPUS}")
        console.print(f"Sonnet Model: {settings.MODEL_SONNET}")
        console.print(f"Haiku Model: {settings.MODEL_HAIKU}")
        console.print(f"Fallback Model: {settings.MODEL_FALLBACK}")
        console.print(f"Temp: {settings.DEFAULT_TEMPERATURE} | Max Tokens: {settings.DEFAULT_MAX_TOKENS} | Effort: {settings.DEFAULT_REASONING_EFFORT}")
        console.print(f"Thinking: {'✅' if settings.ENABLE_THINKING else '❌'} | Optimizations: {'✅' if settings.ENABLE_OPTIMIZATIONS else '❌'}")

    elif args.command == "setup-env":
        setup_env_help()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
