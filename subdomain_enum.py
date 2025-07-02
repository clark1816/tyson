#!/usr/bin/env python3
import subprocess
import sys
import os

# Add Go bin directory to PATH
os.environ['PATH'] = os.environ.get('PATH', '') + ':' + os.path.expanduser('~/go/bin')

def run_subfinder(domain):
    """Run subfinder on the given domain"""
    try:
        print("🔍 Running subfinder...")
        result = subprocess.run(['subfinder', '-d', domain], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error running subfinder: {e}")
        return []
    except FileNotFoundError:
        print("subfinder not found. Please install it first.")
        return []

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

def run_gobuster(domain):
    """Run gobuster to bruteforce common subdomain patterns"""
    try:
        print("🔍 Running gobuster (bruteforce)...")
        # Common subdomain wordlist
        wordlist = [
            "app", "api", "dev", "staging", "test", "admin", "login", "portal",
            "dashboard", "console", "manage", "control", "web", "www", "mail",
            "ftp", "smtp", "pop", "imap", "ns1", "ns2", "dns", "vpn", "remote",
            "secure", "ssl", "cdn", "static", "assets", "media", "files",
            "backup", "db", "database", "sql", "mysql", "postgres", "redis",
            "cache", "proxy", "gateway", "router", "firewall", "loadbalancer",
            "monitor", "status", "health", "metrics", "logs", "analytics",
            "tracking", "stats", "report", "docs", "help", "support", "faq",
            "blog", "news", "forum", "chat", "chatbot", "bot", "crm", "erp",
            "hr", "payroll", "finance", "accounting", "billing", "payment",
            "shop", "store", "cart", "checkout", "order", "inventory",
            "dev-api", "staging-api", "test-api", "prod-api", "internal-api",
            "external-api", "public-api", "private-api", "rest-api", "graphql",
            "soap-api", "webhook", "callback", "oauth", "auth", "sso",
            "staging-login", "dev-login", "test-login", "admin-login",
            "staging-portal", "dev-portal", "test-portal", "admin-portal"
        ]
        
        # Create temporary wordlist file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('\n'.join(wordlist))
            wordlist_file = f.name
        
        # Run gobuster
        cmd = [
            'gobuster', 'dns', '-d', domain, '-w', wordlist_file,
            '-t', '50',  # 50 threads
            '--timeout', '3s'  # 3 second timeout
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Clean up temp file
        import os
        os.unlink(wordlist_file)
        
        if result.returncode == 0:
            # Parse gobuster output
            lines = result.stdout.strip().split('\n')
            subdomains = []
            for line in lines:
                if 'Found:' in line:
                    # Extract subdomain from "Found: subdomain.domain.com"
                    parts = line.split('Found: ')
                    if len(parts) > 1:
                        subdomain = parts[1].strip()
                        subdomains.append(subdomain)
            return subdomains
        else:
            print(f"Gobuster error: {result.stderr}")
            return []
            
    except subprocess.TimeoutExpired:
        print("Gobuster timed out after 5 minutes")
        return []
    except subprocess.CalledProcessError as e:
        print(f"Error running gobuster: {e}")
        return []
    except FileNotFoundError:
        print("gobuster not found. Please install it first.")
        return []

def remove_duplicates(subdomains):
    """Remove duplicate subdomains and empty lines"""
    # Remove empty lines and strip whitespace
    cleaned = [s.strip() for s in subdomains if s.strip()]
    # Remove duplicates while preserving order
    seen = set()
    unique = []
    for subdomain in cleaned:
        if subdomain not in seen:
            seen.add(subdomain)
            unique.append(subdomain)
    return unique

def run_enumeration(domain):
    """Run all tools and combine results"""
    print(f"🎯 Starting subdomain enumeration for: {domain}")
    print("-" * 50)
    
    # Run all tools
    subfinder_results = run_subfinder(domain)
    assetfinder_results = run_assetfinder(domain)
    gobuster_results = run_gobuster(domain)
    
    # Combine results
    all_subdomains = subfinder_results + assetfinder_results + gobuster_results
    
    # Remove duplicates
    unique_subdomains = remove_duplicates(all_subdomains)
    
    # Print results
    print("\n📊 Results:")
    print(f"Subfinder found: {len(subfinder_results)} subdomains")
    print(f"Assetfinder found: {len(assetfinder_results)} subdomains")
    print(f"Gobuster found: {len(gobuster_results)} subdomains")
    print(f"Total unique subdomains: {len(unique_subdomains)}")
    print("-" * 50)
    
    # Print unique subdomains
    for subdomain in unique_subdomains:
        print(subdomain)
    
    # Save to domains.txt file
    output_file = "domains.txt"
    with open(output_file, 'w') as f:
        for subdomain in unique_subdomains:
            f.write(subdomain + '\n')
    
    print(f"\n💾 Results saved to: {output_file}")
    
    return unique_subdomains

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 tyson.py <domain>")
        print("Example: python3 tyson.py example.com")
        sys.exit(1)
    
    domain = sys.argv[1]
    run_enumeration(domain)
