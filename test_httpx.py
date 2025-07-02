#!/usr/bin/env python3
import subprocess
import os

def test_httpx():
    """Simple test to run httpx on domains.txt"""
    
    # Check if domains.txt exists
    if not os.path.exists("domains.txt"):
        print("❌ domains.txt not found!")
        return
    
    # Read domains.txt to see what we're working with
    with open("domains.txt", "r") as f:
        domains = f.readlines()
    
    print(f"📖 Found {len(domains)} domains in domains.txt")
    print(f"📄 First 5 domains: {[d.strip() for d in domains[:5]]}")
    
    # Run httpx command
    cmd = [
        '/home/savyc/go/bin/httpx', '-l', 'domains.txt',
        '-sc',  # Show status codes
        '-title',  # Show page titles
        '-fr',  # Follow redirects
        '-timeout', '10',  # 10 second timeout
        '-t', '50'  # 50 threads
    ]
    
    print(f"\n🔧 Running command: {' '.join(cmd)}")
    print("-" * 80)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        print(f"📊 Return code: {result.returncode}")
        print(f"📄 STDOUT length: {len(result.stdout)} characters")
        print(f"❌ STDERR length: {len(result.stderr)} characters")
        
        if result.stdout:
            print("\n📄 STDOUT (first 1000 chars):")
            print(result.stdout[:1000])
        
        if result.stderr:
            print("\n❌ STDERR:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_httpx() 