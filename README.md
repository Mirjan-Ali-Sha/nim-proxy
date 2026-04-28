# 🚀 NVIDIA NIM Proxy for Claude Code [v1.1.0]
**Created By: [Mirjan Ali Sha](https://github.com/Mirjan-Ali-Sha)**

A professional, high-performance drop-in replacement for the Anthropic API using NVIDIA NIM models. Optimized specifically for the **Claude Code CLI** and **VSCode tools**.

## ✨ Features
- **🛡️ Privacy First**: 100% Locally hosted. No data tracking, no telemetry, and zero log retention.
- **🪶 Ultra Lightweight**: Minimal footprint and dependency-light for maximum speed.
- **⚡ Drop-in Compatible**: Mimics Anthropic's message protocol perfectly.
- **🔄 SSE Stability**: Advanced indexing system to prevent "Content block not found" errors during long reasoning steps.
- **🧠 Native Reasoning**: Streams live "Thinking" blocks from GLM, DeepSeek, and specialized NIM models.
- **🛠️ Sequential Tools**: Fixed tool-hanging issues by ensuring strict block termination and index alignment.
- **🛡️ Robust Fallback**: Instantly retries if primary models fail.
- **🔥 CLI Config**: Manage all your settings directly from your terminal.

---

## 📦 Installation

### 0. Install Claude Code (If you haven't)
Claude Code requires Node.js. Install it globally via npm:
```bash
npm install -g @anthropic-ai/claude-code
```

### 1. Install the Proxy
```bash
# Clone the repository
git clone https://github.com/Mirjan-Ali-Sha/nim-proxy.git
cd nim-proxy

# Install in editable mode
pip install -e .
```

```bash
pip install nim-proxy
```

### 2. Configure Your API Key (Must)
Run the interactive config command:
```bash
nim-proxy config --key your_nvidia_api_key_here
```

### 3. Start the Server
```bash
# Standard mode (Quiet)
nim-proxy start

# Debug mode (Shows request payloads)
nim-proxy start --verbose
```
The proxy will run at `http://localhost:8082` by default.

---

## 🔗 Connecting Claude Code

You need to point Claude Code to this proxy by setting the `ANTHROPIC_BASE_URL` and a dummy API Key.

### One-Liner Quick Connect
#### Windows (PowerShell)
```bash
$env:ANTHROPIC_AUTH_TOKEN="nim-proxy"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; $env:ANTHROPIC_API_KEY="sk-ant-dummy"; claude
```
#### MacOS / Linux (Bash/Zsh)
```bash
export ANTHROPIC_AUTH_TOKEN="nim-proxy" ANTHROPIC_BASE_URL="http://localhost:8082" ANTHROPIC_API_KEY="sk-ant-dummy"; claude
```

### Windows (PowerShell) - Permanent Setup
To set it up for your current session:
```powershell
$env:ANTHROPIC_AUTH_TOKEN="nim-proxy"
$env:ANTHROPIC_BASE_URL="http://localhost:8082"
$env:ANTHROPIC_API_KEY="sk-ant-dummy"
claude
```

**Permanent (Recommended):**
Add these lines to your PowerShell Profile (`notepad $profile`):
```powershell
$env:ANTHROPIC_AUTH_TOKEN="nim-proxy"
$env:ANTHROPIC_BASE_URL="http://localhost:8082"
$env:ANTHROPIC_API_KEY="sk-ant-dummy"
```

### macOS / Linux (Bash or Zsh) 
To set it up for your current session:
```bash
export ANTHROPIC_AUTH_TOKEN="nim-proxy"
export ANTHROPIC_BASE_URL="http://localhost:8082"
export ANTHROPIC_API_KEY="sk-ant-dummy"
claude
```

**Permanent:**
Add these lines to your `~/.bashrc` or `~/.zshrc`:
```bash
export ANTHROPIC_AUTH_TOKEN="nim-proxy"
export ANTHROPIC_BASE_URL="http://localhost:8082"
export ANTHROPIC_API_KEY="sk-ant-dummy"
```

---

## 🛠️ CLI Help
Use the built-in help setup generator:
```bash
nim-proxy --help
```

```bash
nim-proxy config --help
```

```bash
nim-proxy setup-env
```


To update model mappings:
```bash
nim-proxy config --opus deepseek-ai/deepseek-v4-pro --sonnet openai/gpt-oss-120b --haiku z-ai/glm-5.1 --fallback openai/gpt-oss-20b
```

## 📜 License
MIT
