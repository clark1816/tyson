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

🧰 Subdomain Enumeration Usage
🔹 Basic Usage

python3 subdomain_enum.py -t example.com

This will:
- Run subfinder, assetfinder, and gobuster
- Combine and deduplicate all found subdomains
- Save the unique subdomains to `domains.txt`
- Print summary statistics and the list of subdomains to your terminal



## Output Structure

Results are organized in timestamped directories under `results/`:

```
results/
├── domain.com_20240101_123456/
│   ├── domains.txt              # All discovered subdomains
│   ├── live_subdomains.txt      # Clean list of live URLs
│   └── detailed_results.txt     # Detailed analysis (if -d flag used)
```

## Important Notes

### 403 Status Code Warning ⚠️

**False 403 Responses**: You may encounter 403 (Forbidden) status codes that should actually be 200 (OK). This is commonly caused by:

- **WAF Protection**: Web Application Firewalls blocking automated requests
- **Bot Detection**: Anti-bot measures that block scripted access
- **Rate Limiting**: Server-side protection against rapid requests

**This is NOT a vulnerability** - it's actually a **security feature** of the target website. These 403 responses often indicate:
- The subdomain is live and functional
- The site has proper security measures in place
- Manual browser testing would likely show the actual content

**Recommendation**: If you encounter 403 responses on important subdomains, manually test them in a browser to see the actual content and functionality.

### Rate Limiting

The tool includes built-in rate limiting (50 requests/sec) to:
- Prevent overwhelming target servers
- Reduce the likelihood of being blocked
- Maintain ethical reconnaissance practices

## Requirements

- Python 3.x
- Go language (for installing tools)
- subfinder: `go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest`
- assetfinder: `go install github.com/tomnomnom/assetfinder@latest`
- gobuster: `sudo apt install gobuster`
- httpx: `go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest`

Make sure your Go bin directory is in your PATH:
```bash
export PATH=$PATH:~/go/bin
```
