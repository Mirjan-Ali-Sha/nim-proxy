# 🚀 nim-proxy
**Created By: [Mirjan Ali Sha](https://github.com/Mirjan-Ali-Sha)**

A professional, high-performance drop-in replacement for the Anthropic API using NVIDIA NIM models. Optimized specifically for the **Claude Code CLI** and **VSCode tools**.

## ✨ Features
- **🛡️ Privacy First**: 100% Locally hosted. No data tracking, no telemetry, and zero log retention.
- **🪶 Ultra Lightweight**: Minimal footprint and dependency-light for maximum speed.
- **⚡ Drop-in Compatible**: Mimics Anthropic's message protocol perfectly.
- **🧠 Native Reasoning**: Streams live "Thinking" blocks from GLM and DeepSeek models.
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

### 2. Configure Your API Key (Must)
Run the interactive config command:
```bash
nim-proxy config --key your_nvidia_api_key_here
```

### 3. Start the Server
```bash
nim-proxy start
```
The proxy will run at `http://localhost:8082`.

---

## 🔗 Connecting Claude Code

You need to point Claude Code to this proxy by setting the `ANTHROPIC_BASE_URL` and a dummy API Key.

### Manual Setup
#### Windows (PowerShell)
```bash
$env:ANTHROPIC_AUTH_TOKEN="nim-proxy"; $env:ANTHROPIC_API_KEY="sk-ant-dummy"; $env:ANTHROPIC_BASE_URL="http://localhost:8082"; claude
```
#### MacOS / Linux (Bash/Zsh)
```bash
export ANTHROPIC_AUTH_TOKEN="nim-proxy"; export ANTHROPIC_API_KEY="sk-ant-dummy"; export ANTHROPIC_BASE_URL="http://localhost:8082"; claude
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
