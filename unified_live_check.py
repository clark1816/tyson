#!/usr/bin/env python3
import subprocess
import os
import argparse
import re
from datetime import datetime

def run_command(cmd, output_file=None):
    """Run a shell command and save output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if output_file:
            with open(output_file, "w") as f:
                f.write(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[!] Error running '{cmd}': {e}")
        print(f"[!] stderr: {e.stderr}")
        return ""
    except FileNotFoundError:
        print(f"[!] httpx not found. Please install it: go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest")
        return ""

def create_output_dir(target):
    """Create a timestamped results directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"results/{target}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

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
    
    for line in output.splitlines():
        if line.strip():
            if detailed:
                # JSON output for detailed mode
                try:
                    # Extract URL, status code, title, and technologies from JSON
                    import json
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
    live_file = f"{output_dir}/live_subdomains.txt"
    if live_subdomains:
        with open(live_file, "w") as f:
            for url in live_subdomains:
                f.write(url + "\n")
    
    # Save detailed results (excluding redirects, no color codes) if requested
    if detailed and detailed_output:
        detailed_file = f"{output_dir}/detailed_results.txt"
        with open(detailed_file, "w") as f:
            f.write("\n".join(detailed_output) + "\n")
    
    return live_subdomains, status_codes

def main():
    parser = argparse.ArgumentParser(description="Live Subdomain Check for Bug Bounty")
    parser.add_argument("-t", "--target", required=True, help="Target domain (e.g., example.com)")
    parser.add_argument("-i", "--input", required=True, help="Input file with subdomains (e.g., domains.txt)")
    parser.add_argument("-d", "--detailed", action="store_true", help="Include detailed output with titles, tech detection, and versions (excludes redirects)")
    args = parser.parse_args()

    target = args.target
    input_file = args.input
    print(f"[+] Starting live subdomain check for {target}")

    # Setup output
    output_dir = create_output_dir(target)

    # Run httpx
    live_subdomains, status_codes = run_httpx(input_file, output_dir, args.detailed)

    # Print results
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
    
    print(f"\n💾 Clean URLs saved to: {output_dir}/live_subdomains.txt")
    if args.detailed:
        print(f"📋 Detailed results (excluding redirects) saved to: {output_dir}/detailed_results.txt")

if __name__ == "__main__":
    main()