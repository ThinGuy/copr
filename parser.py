#!/usr/bin/env python3
# Ubuntu Repository Parser
# Revision: 1.0.3
# Fix: Handle missing 'Package' field gracefully and skip invalid files

import gzip
import requests
import json
import sys
from io import BytesIO
import argparse
import concurrent.futures

# Argument parsing
parser = argparse.ArgumentParser(description='Parse Ubuntu Packages.gz files')
parser.add_argument('url', nargs='?', help='URL of the Packages.gz file')
parser.add_argument('-i', '--index-file', help='Path to ubuntu_indexes.json to process multiple indexes')
parser.add_argument('-o', '--output', default='ubuntu_packages.json', help='Output JSON filename')
parser.add_argument('--stdout', action='store_true', help='Output JSON to stdout instead of file')
parser.add_argument('--validate', action='store_true', help='Validate URLs')

args = parser.parse_args()

# Function to process a single Packages.gz file
def process_packages_gz(url, release):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if len(response.content) == 0:
            print(f"Skipping empty file: {url}")
            return []
        
        with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8') as f:
            packages_data = f.read()
        
        if not packages_data.strip():
            print(f"Skipping zero-byte or unreadable file: {url}")
            return []
    except requests.RequestException as e:
        print(f"Skipping due to download error: {url} - {e}")
        return []
    
    packages = packages_data.strip().split("\n\n")
    parsed_packages = []
    
    for pkg in packages:
        pkg_dict = {"release": release}  # Include release info
        lines = pkg.strip().split("\n")
        for line in lines:
            if line.startswith("Package: "):
                pkg_dict["package"] = line.split("Package: ")[1]
            elif line.startswith("Version: "):
                version = line.split("Version: ")[1]
                pkg_dict["version"] = version.split(":")[-1]
            elif line.startswith("Source: "):
                pkg_dict["source"] = line.split("Source: ")[1].split()[0]
            elif line.startswith("Section: "):
                pkg_dict["section"] = line.split("Section: ")[1]
            elif line.startswith("Maintainer: "):
                pkg_dict["maintainer"] = line.split("Maintainer: ")[1]
            elif line.startswith("Size: "):
                pkg_dict["size"] = int(line.split("Size: ")[1])
        
        # Ensure 'package' field exists before setting default source
        if "package" not in pkg_dict:
            print(f"Skipping entry with missing 'Package' field: {pkg_dict}")
            continue
        
        pkg_dict.setdefault("source", pkg_dict["package"])
        
        if "package" in pkg_dict and "version" in pkg_dict:
            version_clean = pkg_dict['version'].split(":")[-1]
            source_initial = pkg_dict["source"][:4] if pkg_dict["source"].startswith("lib") else pkg_dict["source"][0]
            base_url = f"https://changelogs.ubuntu.com/changelogs/pool/main/{source_initial}/{pkg_dict['source']}/{pkg_dict['source']}_{version_clean}"
            pkg_dict["copyright"] = f"{base_url}/copyright"
            pkg_dict["changelog"] = f"{base_url}/changelog"
            parsed_packages.append(pkg_dict)
    
    return parsed_packages

all_packages = []

if args.index_file:
    with open(args.index_file, "r") as f:
        index_data = json.load(f)
    
    for entry in index_data:
        print(f"Processing: {entry['index_url']}")
        try:
            all_packages.extend(process_packages_gz(entry['index_url'], entry['release']))
        except requests.RequestException as e:
            print(f"Failed to fetch {entry['index_url']}: {e}")

elif args.url:
    all_packages = process_packages_gz(args.url, "manual")
else:
    print("Error: Either a URL or an index file must be provided.")
    sys.exit(1)

# Output JSON
if args.stdout:
    print(json.dumps(all_packages, indent=2))
else:
    with open(args.output, "w") as f:
        json.dump(all_packages, f, indent=2)
    print(f"Data successfully saved to {args.output}")

