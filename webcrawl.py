#!/usr/bin/env python3
import subprocess
import os
import argparse
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
        print(f"[!] katana not found. Please install it: go install github.com/projectdiscovery/katana/cmd/katana@latest")
        return ""

def create_output_dir(target):
    """Create a timestamped results directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"results/{target}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def web_crawl(input_file, output_dir):
    """Crawl URLs with katana."""
    print(f"[*] Crawling URLs from {input_file}...")
    crawl_file = f"{output_dir}/crawled_urls.txt"
    katana_cmd = f"katana -list {input_file} -concurrency 10 -silent -jc -output {crawl_file}"
    run_command(katana_cmd, crawl_file)
    if os.path.exists(crawl_file):
        with open(crawl_file) as f:
            return [line.strip() for line in f if line.strip()]
    return []

def main():
    parser = argparse.ArgumentParser(description="Web Crawling for Bug Bounty")
    parser.add_argument("-t", "--target", required=True, help="Target domain (e.g., doctolib.fr)")
    parser.add_argument("-i", "--input", required=True, help="Input file with subdomains (e.g., live_subdomains.txt)")
    args = parser.parse_args()

    target = args.target
    input_file = args.input
    print(f"[+] Starting web crawling for {target}")

    # Setup output
    output_dir = create_output_dir(target)

    # Run crawl
    crawled_urls = web_crawl(input_file, output_dir)

    # Print results
    print(f"\n📊 Results: {len(crawled_urls)} URLs found")
    print("\n🌐 Crawled URLs (first 10):")
    for url in crawled_urls[:10]:
        print(url)
    if len(crawled_urls) > 10:
        print("...")
    print(f"\n💾 Results saved to: {output_dir}/crawled_urls.txt")

if __name__ == "__main__":
    main()