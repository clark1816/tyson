# tyson
All in one tool for doing recon.

# Subdomain Enumeration Toolkit

This toolkit uses subfinder, assetfinder, and gobuster to enumerate subdomains for a given target domain.

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

### Step 2: HTTP Reconnaissance

After generating the subdomain list, use httpx to check which domains are live:

```bash
httpx -l domains.txt -sc -title -fr -timeout 10 -t 50 -o httpx_results.txt
```

**What this does:**
- `-l domains.txt` - Reads domains from your file
- `-sc` - Shows status codes
- `-title` - Shows page titles
- `-fr` - Follows redirects
- `-timeout 10` - 10 second timeout per request
- `-t 50` - 50 threads for speed
- `-o httpx_results.txt` - Saves results to a file

**For more detailed recon:**
```bash
httpx -l domains.txt -sc -title -tech-detect -fr -timeout 10 -t 50 -o httpx_detailed.txt
```

This adds `-tech-detect` to identify technologies used on each site.

**To filter for specific status codes:**
```bash
httpx -l domains.txt -sc -title -fr -mc 200,301,302,403 -o live_domains.txt
```

This only shows domains with status codes 200, 301, 302, or 403.

You can then use `httpx` or another tool to check which subdomains are live using the generated `domains.txt` file.
