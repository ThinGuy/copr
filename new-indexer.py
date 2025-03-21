#!/usr/bin/env python3
"""
Ubuntu Repo Indexer
Version: 1.1.0
Description: Generates `ubuntu_repo_indexes.json` with index URLs and metadata.
"""

import requests
from bs4 import BeautifulSoup
import json
import argparse
from datetime import datetime
from requests.adapters import HTTPAdapter, Retry

SCRIPT_VERSION = "1.1.0"

# Configure HTTP session with retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

def log(msg, verbose=False):
    if verbose:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_suites(dist_url, verbose=False):
    try:
        response = session.get(dist_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return [link.get('href').rstrip('/') for link in soup.find_all('a')
                if link.get('href') and link.get('href').endswith('/')
                and not link.get('href').startswith('../')]
    except requests.RequestException as e:
        log(f"❌ Failed to fetch suites from {dist_url} - {e}", verbose)
        return []

def parse_suite_name(suite):
    if '-' in suite:
        release, pocket = suite.split('-', 1)
    else:
        release, pocket = suite, ''
    return release, pocket

def build_index(dist_urls, verbose=False):
    results = []
    for dist_url in dist_urls:
        suites = get_suites(dist_url, verbose)
        for suite in suites:
            release, pocket = parse_suite_name(suite)
            index_url = f"{dist_url}/{suite}/main/binary-amd64/Packages.gz"
            results.append({
                "dist_url": dist_url,
                "index_type": "package",
                "release": release,
                "pocket": pocket,
                "suite": suite,
                "component": "main",
                "architecture": "amd64",
                "index_url": index_url
            })
            log(f"✔️ Added index: {index_url}", verbose)
    return results

def main():
    parser = argparse.ArgumentParser(description='Ubuntu Repo Indexer')
    parser.add_argument('-u', '--ubuntu', action='store_true', help='Use standard Ubuntu repo URLs')
    parser.add_argument('-o', '--output', default='ubuntu_repo_indexes.json', help='Output JSON filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode for detailed progress information')
    args = parser.parse_args()

    dist_urls = [
        "https://archive.ubuntu.com/ubuntu/dists/",
        "https://ports.ubuntu.com/ubuntu-ports/dists/",
        "https://esm.ubuntu.com/apps/ubuntu/dists/",
        "https://esm.ubuntu.com/cc/ubuntu/dists/",
        "https://esm.ubuntu.com/cis/ubuntu/dists/",
        "https://esm.ubuntu.com/fips-preview/ubuntu/dists/",
        "https://esm.ubuntu.com/fips-updates/ubuntu/dists/",
        "https://esm.ubuntu.com/fips/ubuntu/dists/",
        "https://esm.ubuntu.com/infra-legacy/ubuntu/dists/",
        "https://esm.ubuntu.com/infra/ubuntu/dists/",
        "https://esm.ubuntu.com/realtime/ubuntu/dists/",
        "https://esm.ubuntu.com/ros-updates/ubuntu/dists/",
        "https://esm.ubuntu.com/ros/ubuntu/dists/",
        "https://esm.ubuntu.com/usg/ubuntu/dists/",
        "https://archive.anbox-cloud.io/stable/dists/"
    ] if args.ubuntu else []

    index_data = build_index(dist_urls, args.verbose)
    
    output_data = {
        "generated_at": datetime.now().isoformat(),
        "script_version": SCRIPT_VERSION,
        "indexes": index_data
    }

    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"✅ Data successfully written to {args.output}")

if __name__ == "__main__":
    main()

