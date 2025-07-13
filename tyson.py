#!/usr/bin/env python3
import subprocess
import os
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
import tempfile

# Default wordlists (add more paths here or via --wordlists)
WORDLISTS = ["wordlists/common_subdomains.txt"]

def run_command(cmd, output_file=None):
    """Run a shell command and save output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if output_file:
            with open(output_file, "w") as f:
                f.write(result.stdout)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"[!] Error running '{cmd}': {e}")
        print(f"[!] stderr: {e.stderr}")
        return []
    except FileNotFoundError:
        print(f"[!] Tool not found for '{cmd}'. Ensure it’s installed.")
        return []

def create_output_dir(target):
    """Create a timestamped results directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"results/{target}_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def run_subfinder(domain):
    """Run subfinder on the given domain."""
    print("🔍 Running subfinder...")
    subfinder_cmd = f"subfinder -d {domain} -silent"
    results = run_command(subfinder_cmd)
    unique_results = list(set(results))
    print(f"[+] Subfinder found {len(unique_results)} unique subdomains")
    return unique_results

def run_assetfinder(domain):
    """Run assetfinder on the given domain"""
    try:
        print("🔍 Running assetfinder...")
        result = subprocess.run(['assetfinder', domain], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error running assetfinder: {e}")
        return []
    except FileNotFoundError:
        print("assetfinder not found. Please install it first.")
        return []

def run_crtsh(domain):
    """Fetch subdomains from crt.sh using curl."""
    print("🔍 Running crt.sh...")
    crtsh_cmd = f"curl -s 'https://crt.sh/?q=%.{domain}&output=json' | jq -r '.[].name_value' | grep -Po '(\\w+\\.\\w+\\.\\w+)' | sort -u"
    results = run_command(crtsh_cmd)
    unique_results = list(set(results))
    print(f"[+] crt.sh found {len(unique_results)} unique subdomains")
    return unique_results

def run_gobuster(domain, wordlists, output_dir):
    """Run gobuster with multiple wordlists in line-by-line format."""
    print("🔍 Running gobuster (bruteforce)...")
    subdomains = set()

    for wordlist in wordlists:
        wordlist_path = Path(wordlist)
        if not wordlist_path.exists():
            print(f"[!] Wordlist not found: {wordlist}")
            continue

        # Read wordlist (line-by-line format)
        with open(wordlist_path) as f:
            wordlist_items = [line.strip() for line in f if line.strip()]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=True) as temp_file:
            # Write wordlist items to temporary file (one per line)
            temp_file.write("\n".join(wordlist_items))
            temp_file.flush()

            # Run gobuster
            gobuster_output_file = output_dir / f"gobuster_{wordlist_path.name}_temp.txt"
            gobuster_cmd = (
                f"gobuster dns -d {domain} -w {temp_file.name} -t 50 --timeout 15s "
                f"-o {gobuster_output_file}"
            )
            result = run_command(gobuster_cmd, gobuster_output_file)

            # Debugging: Print gobuster output
            if result:
                print(f"[*] Gobuster output for {wordlist}: {result[:5]}")

            if gobuster_output_file.exists():
                with open(gobuster_output_file) as f:
                    gobuster_subdomains = [line.split()[-1] for line in f if line.strip() and "Found:" in line]
                subdomains.update(gobuster_subdomains)
                gobuster_output_file.unlink()

    print(f"[+] Gobuster found {len(subdomains)} unique subdomains")
    return list(subdomains)

def remove_duplicates(subdomains):
    """Remove duplicate subdomains and empty lines."""
    cleaned = [s.strip() for s in subdomains if s.strip()]
    seen = set()
    unique = []
    for subdomain in cleaned:
        if subdomain not in seen:
            seen.add(subdomain)
            unique.append(subdomain)
    return unique

def subdomain_enum(domain, wordlists, output_dir):
    """Perform subdomain enumeration."""
    print(f"🎯 Starting subdomain enumeration for: {domain}")
    print("-" * 50)

    # Run all tools
    subfinder_results = run_subfinder(domain)
    assetfinder_results = run_assetfinder(domain)
    crtsh_results = run_crtsh(domain)
    gobuster_results = run_gobuster(domain, wordlists, output_dir)

    # Combine results
    all_subdomains = subfinder_results + assetfinder_results + crtsh_results + gobuster_results

    # Remove duplicates
    unique_subdomains = remove_duplicates(all_subdomains)

    # Save to domains.txt
    domains_file = output_dir / "domains.txt"
    with open(domains_file, "w") as f:
        for subdomain in sorted(unique_subdomains):
            f.write(subdomain + "\n")

    # Print results
    print("\n📊 Results:")
    print(f"Subfinder found: {len(subfinder_results)} unique subdomains")
    print(f"Assetfinder found: {len(assetfinder_results)} unique subdomains")
    print(f"crt.sh found: {len(crtsh_results)} unique subdomains")
    print(f"Gobuster found: {len(gobuster_results)} unique subdomains")
    print(f"Total unique subdomains: {len(unique_subdomains)}")
    print(f"\n💾 Results saved to: {domains_file}")

    return domains_file

def run_httpx(input_file, output_dir, detailed=False):
    """Check live subdomains with httpx."""
    print(f"[*] Checking live subdomains from {input_file}...")
    
    # Check if input file exists and is not empty
    if not os.path.exists(input_file) or os.path.getsize(input_file) == 0:
        print(f"[!] Input file {input_file} is empty or missing")
        return [], {}
    
    # Base httpx command with rate limiting
    base_cmd = f"httpx -l {input_file} -sc -fr -timeout 10 -t 50 -rl 50"
    
    if detailed:
        base_cmd += " -title -td -json"  # Add title, tech detection, and JSON output for versions
    
    # Run httpx and capture output
    output = run_command(base_cmd)
    
    # Parse results
    live_subdomains = []
    status_codes = {}
    detailed_output = []
    
    for line in output:
        if line.strip():
            if detailed:
                # JSON output for detailed mode
                try:
                    # Extract URL, status code, title, and technologies from JSON
                    data = json.loads(line)
                    url = data.get("url", "").strip()
                    status_code = data.get("status_code", "Unknown")
                    title = data.get("title", "No Title")
                    techs = data.get("technologies", [])
                    version_info = ", ".join([f"{tech['name']} {tech.get('version', '')}".strip() for tech in techs if tech.get("version")])
                    tech_list = ", ".join([tech["name"] for tech in techs])
                    
                    if url:
                        live_subdomains.append(url)
                        status_codes[url] = status_code
                        # Exclude redirects (301/302) from detailed output
                        if status_code not in [301, 302]:
                            clean_line = f"{url} [{status_code}] [{title}] [{tech_list}]"
                            if version_info:
                                clean_line += f" [Versions: {version_info}]"
                            detailed_output.append(clean_line)
                except json.JSONDecodeError:
                    continue
            else:
                # Non-detailed mode: parse standard output
                if " [" in line and "]" in line:
                    url = line.split(" [")[0].strip()
                    status_part = line.split(" [")[1].split("]")[0]
                    try:
                        status_code = int(status_part) if status_part.isdigit() else status_part
                        live_subdomains.append(url)
                        status_codes[url] = status_code
                    except ValueError:
                        continue
    
    # Save clean URLs to file
    live_file = output_dir / "live_subdomains.txt"
    if live_subdomains:
        with open(live_file, "w") as f:
            for url in live_subdomains:
                f.write(url + "\n")
    
    # Save detailed results (excluding redirects, no color codes) if requested
    if detailed and detailed_output:
        detailed_file = output_dir / "detailed_results.txt"
        with open(detailed_file, "w") as f:
            f.write("\n".join(detailed_output) + "\n")
    
    print(f"\n📊 Results: {len(live_subdomains)} live subdomains found")
    print("\n🌐 Live Subdomains:")
    
    for url in live_subdomains:
        status = status_codes.get(url, "Unknown")
        if status == 403:
            print(f"{url} [{status}] 🚨 (403 - try bypassing!)")
        elif status == 200:
            print(f"{url} [{status}] ✅")
        else:
            print(f"{url} [{status}]")
    
    print(f"\n💾 Clean URLs saved to: {live_file}")
    if detailed:
        print(f"📋 Detailed results (excluding redirects) saved to: {detailed_file}")

    return live_file

def web_crawl(input_file, output_dir):
    """Crawl URLs with katana."""
    print(f"[*] Crawling URLs from {input_file}...")
    crawl_file = output_dir / "crawled_urls.txt"
    katana_cmd = f"katana -list {input_file} -concurrency 10 -silent -jc -output {crawl_file}"
    run_command(katana_cmd, crawl_file)
    if os.path.exists(crawl_file):
        with open(crawl_file) as f:
            crawled_urls = [line.strip() for line in f if line.strip()]
        print(f"\n📊 Results: {len(crawled_urls)} URLs found")
        print("\n🌐 Crawled URLs (first 10):")
        for url in crawled_urls[:10]:
            print(url)
        if len(crawled_urls) > 10:
            print("...")
        print(f"\n💾 Results saved to: {crawl_file}")
        return crawl_file
    return None

def main():
    parser = argparse.ArgumentParser(description="Tyson All-in-One Recon Toolkit")
    parser.add_argument("-t", "--target", required=True, help="Target domain (e.g., tesla.com)")
    parser.add_argument("-s", action="store_true", help="Perform subdomain enumeration")
    parser.add_argument("-l", action="store_true", help="Perform live subdomain check")
    parser.add_argument("-wc", action="store_true", help="Perform web crawling")
    parser.add_argument("-d", action="store_true", help="Enable detailed mode for live check")
    parser.add_argument("-w", "--wordlists", help="Comma-separated list of wordlists (e.g., wordlists/list1.txt,wordlists/list2.txt)")
    parser.add_argument("-i", "--input", help="Input file for live check or web crawl (e.g., domains.txt)")
    args = parser.parse_args()

    target = args.target
    print(f"[+] Starting Tyson recon for {target}")

    # Setup output
    output_dir = create_output_dir(target)

    if args.s:
        subdomain_enum(target, WORDLISTS + (args.wordlists.split(",") if args.wordlists else []), output_dir)

    if args.l:
        if not args.input:
            print(f"[!] Input file required for live check. Use -i domains.txt")
            return
        run_httpx(args.input, output_dir, args.d)

    if args.wc:
        if not args.input:
            print(f"[!] Input file required for web crawl. Use -i live_subdomains.txt")
            return
        web_crawl(args.input, output_dir)

if __name__ == "__main__":
    main()