# 🥊 Tyson — All-in-One Recon Toolkit

**Tyson** is a modular recon automation framework combining `subfinder`, `assetfinder`, `gobuster`, and `httpx` for comprehensive subdomain discovery and live checking.

---

## 🚀 Features

- 🔍 Subdomain enumeration via multiple tools (subfinder, assetfinder, gobuster)
- 🌐 Live status checking with status code breakdown
- 🧠 Detailed mode: tech stack, page titles, version info
- 🗂️ Organized, timestamped result directories
- 🛡️ Rate-limiting built-in (50 req/sec)

---

## 📦 Installation

### Requirements

- **Python 3.x**
- **Go (latest)**
- Tools:
  ```bash
  go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
  go install github.com/tomnomnom/assetfinder@latest
  sudo apt install gobuster
  go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
