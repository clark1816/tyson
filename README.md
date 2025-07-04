# tyson
All in one tool for doing recon.

# Subdomain Enumeration Toolkit

This toolkit provides a comprehensive subdomain enumeration and live checking solution using subfinder, assetfinder, gobuster, and httpx.

## Features

- **Subdomain Discovery**: Uses multiple tools (subfinder, assetfinder, gobuster) for comprehensive coverage
- **Live Checking**: Automated httpx scanning with status codes and filtering
- **Detailed Analysis**: Optional detailed mode with titles, technology detection, and version information
- **Organized Output**: Timestamped results directories for easy management
- **Rate Limiting**: Built-in protection to prevent overwhelming target servers

## Usage

### Step 1: Subdomain Enumeration

To enumerate subdomains and save them to `domains.txt`:

```bash
python3 subdomain_enum.py <target-domain>
```

**Example:**

```bash
python3 subdomain_enum.py canterbury.ac.nz
```

This will:
- Run subfinder, assetfinder, and gobuster
- Combine and deduplicate all found subdomains
- Save the unique subdomains to `domains.txt`
- Print summary statistics and the list of subdomains to your terminal

### Step 2: Live Subdomain Checking

After generating the subdomain list, use the unified live check script:

#### Basic Live Checking

```bash
python3 unified_live_check.py -t <target-domain> -i domains.txt
```

**Example:**

```bash
python3 unified_live_check.py -t canterbury.ac.nz -i domains.txt
```

This will:
- Check all subdomains for live status
- Save clean URLs to `live_subdomains.txt`
- Show status code summary
- Apply rate limiting (50 requests/sec) to be respectful to target servers

#### Detailed Analysis Mode

For comprehensive reconnaissance with technology detection:

```bash
python3 unified_live_check.py -t <target-domain> -i domains.txt -d
```

**The detailed mode (`-d` flag) provides:**
- Page titles for each live subdomain
- Technology detection (frameworks, CMS, servers, etc.)
- Version information when available
- Excludes redirects (301/302) for cleaner results
- Saves detailed analysis to `detailed_results.txt`

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

## Command Reference

### Subdomain Enumeration
```bash
python3 subdomain_enum.py <domain>
```

### Live Checking - Basic
```bash
python3 unified_live_check.py -t <domain> -i <input-file>
```

### Live Checking - Detailed
```bash
python3 unified_live_check.py -t <domain> -i <input-file> -d
```

## Example Workflow

```bash
# 1. Discover subdomains
python3 subdomain_enum.py example.com

# 2. Check which ones are live (basic)
python3 unified_live_check.py -t example.com -i domains.txt

# 3. Or get detailed analysis
python3 unified_live_check.py -t example.com -i domains.txt -d
```

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
