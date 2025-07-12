#!/usr/bin/env python3
import subprocess
import argparse
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
            output_file.write_text(result.stdout)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"[!] Error running '{cmd}': {e.stderr}")
        return []
    except FileNotFoundError:
        print(f"[!] Tool not found for '{cmd}'. Ensure it’s installed.")
        return []

def create_output_dir(target):
    """Create a timestamped results directory with readable format (YYYY-MM-DD_HH:MM:SS EDT)."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S %Z")
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

def run_enumeration(domain, wordlists, output_dir):
    """Run all tools and combine results."""
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

    return unique_subdomains

def main():
    parser = argparse.ArgumentParser(description="Subdomain Enumeration for Bug Bounty")
    parser.add_argument("-t", "--target", required=True, help="Target domain (e.g., example.com)")
    parser.add_argument("-w", "--wordlists", help="Comma-separated list of wordlists (e.g., wordlists/list1.txt,wordlists/list2.txt)")
    args = parser.parse_args()

    target = args.target
    # Deduplicate wordlists
    wordlists = list(set(WORDLISTS + (args.wordlists.split(",") if args.wordlists else [])))

    print(f"[+] Starting subdomain enumeration for {target}")
    print(f"[+] Using wordlists: {', '.join(wordlists)}")

    # Setup output
    output_dir = create_output_dir(target)

    # Run enumeration
    run_enumeration(target, wordlists, output_dir)

if __name__ == "__main__":
    main()