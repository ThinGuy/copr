#!/usr/bin/env python3
"""
Ubuntu Package Information Parser
Version: 1.1.0
Description: Parses Ubuntu package data, extracts license info, and maps SPDX identifiers.
"""

import requests
import json
import re
import argparse
from concurrent.futures import ThreadPoolExecutor
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

def fetch_text(url, verbose=False):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        log(f"✔️ Fetched: {url}", verbose)
        return response.text
    except requests.RequestException as e:
        log(f"⚠️ Failed to fetch: {url} - {e}", verbose)
        return ""

def extract_licenses(text):
    spdx_mapping = {
        "MIT License": "MIT",
        "GNU General Public License v3.0": "GPL-3.0-only",
        "Apache License 2.0": "Apache-2.0",
        "BSD 3-Clause License": "BSD-3-Clause",
        "LGPL-3.0": "LGPL-3.0-only",
        "Mozilla Public License 2.0": "MPL-2.0",
        "Eclipse Public License 2.0": "EPL-2.0"
    }

    detected_licenses = []
    for license_name, spdx_id in spdx_mapping.items():
        if re.search(license_name, text, re.IGNORECASE):
            detected_licenses.append(spdx_id)
    return list(set(detected_licenses))  # Remove duplicates

def process_entry(entry, verbose=False):
    package_info = {
        "package": entry.get("package"),
        "version": entry.get("version"),
        "release": entry.get("release"),
        "copyright_url": entry["index_url"].replace("Packages.gz", "copyright"),
        "changelog_url": entry["index_url"].replace("Packages.gz", "changelog")
    }

    copyright_text = fetch_text(package_info["copyright_url"], verbose)
    package_info["licenses"] = extract_licenses(copyright_text)

    return package_info

def main():
    parser = argparse.ArgumentParser(description='Ubuntu Package Information Parser')
    parser.add_argument('-i', '--index-file', required=True, help='Path to ubuntu_repos.json')
    parser.add_argument('-o', '--output', default='ubuntu_packages.json', help='Output JSON filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
    args = parser.parse_args()

    with open(args.index_file, 'r') as f:
        index_data = json.load(f).get("indexes", [])

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda entry: process_entry(entry, args.verbose), index_data))

    output_data = {
        "generated_at": datetime.now().isoformat(),
        "script_version": SCRIPT_VERSION,
        "packages": results
    }

    with open(args.output, 'w') as f:
        json.dump(output_data, f, indent=2)
    print(f"✅ Data successfully written to {args.output}")

if __name__ == "__main__":
    main()

