# tyson
All in one tool for doing recon.

# Subdomain Enumeration Toolkit

This toolkit uses subfinder, assetfinder, and gobuster to enumerate subdomains for a given target domain.

## Usage

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

You can then use `httpx` or another tool to check which subdomains are live using the generated `domains.txt` file.
