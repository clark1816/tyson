🥊 Tyson — All-in-One Recon Toolkit
Tyson is a modular recon automation framework combining subfinder, assetfinder, crt.sh, and gobuster for comprehensive subdomain discovery, along with httpx for live checking and katana for web crawling.

🚀 Features

🔍 Subdomain enumeration via multiple tools (subfinder, assetfinder, crt.sh, gobuster)
🌐 Live status checking with status code breakdown
🧠 Detailed mode: tech stack, page titles, version info
🗂️ Organized, timestamped result directories (e.g., results/tesla.com_20250712_220505 EDT)
🛡️ Rate-limiting built-in (50 req/sec)


📦 Installation
Requirements

Python 3.x
Go (latest)
Tools:go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/tomnomnom/assetfinder@latest
sudo apt install gobuster curl jq grep
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install github.com/projectdiscovery/katana/cmd/katana@latest




🚦 Usage
Tyson combines subdomain enumeration, live checking, and web crawling into a single script with CLI options.
Subdomain Enumeration

Command: python tyson.py -s <domain>
Example: python tyson.py -s tesla.com
Description: Runs subfinder, assetfinder, crt.sh, and gobuster to enumerate subdomains.
Output: results/<domain>_<timestamp>/domains.txt

Live Subdomain Check

Command: python tyson.py -l -i <input_file> [-d]
Example: python tyson.py -l -i results/tesla.com_20250712_220505 EDT/domains.txt
Optional: -d for detailed mode (titles, tech, versions).
Description: Checks live status of subdomains from the input file.
Output: results/<domain>_<timestamp>/live_subdomains.txt and detailed_results.txt (if -d).

Web Crawling

Command: python tyson.py -wc -i <input_file>
Example: python tyson.py -wc -i results/tesla.com_20250712_220505 EDT/live_subdomains.txt
Description: Crawls live URLs using katana.
Output: results/<domain>_<timestamp>/crawled_urls.txt

Additional Options

-w <wordlists>: Comma-separated list of wordlists (e.g., wordlists/list1.txt,wordlists/list2.txt) for gobuster.
Example: python tyson.py -s tesla.com -w wordlists/custom.txt


📋 Example Workflow
# 1. Enumerate subdomains
python tyson.py -s tesla.com

# 2. Check live subdomains (basic)
python tyson.py -l -i results/tesla.com_20250712_220505 EDT/domains.txt

# 3. Check live subdomains (detailed)
python tyson.py -l -d -i results/tesla.com_20250712_220505 EDT/domains.txt

# 4. Web crawl
python tyson.py -wc -i results/tesla.com_20250712_220505 EDT/live_subdomains.txt

Replace <timestamp> with the actual directory name from your run.

⚠️ Important Notes

Assetfinder Variance: Results may vary due to external source updates.
403 Status Codes: May indicate WAFs or bot protection; manually test in a browser.
Rate Limiting: Built-in at 50 req/sec to ensure ethical usage.
Ethical Use: Use only on authorized targets (e.g., bug bounty programs).


📚 Requirements

Python 3.x
Go
Tools: subfinder, assetfinder, gobuster, httpx, katana, curl, jq, grep
