#!/usr/bin/env python3
# Ubuntu Repository Sizer
# Revision: 1.0.3

import gzip
import requests
import json
import sys
from io import BytesIO
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description='Ubuntu Repository Sizer')
parser.add_argument('-i', '--index-file', required=True, help='Path to ubuntu_indexes.json')
parser.add_argument('-o', '--output', default='ubuntu_reposize.json', help='Output JSON filename')
args = parser.parse_args()

# Function to process a Packages.gz file
def process_packages_gz(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if len(response.content) == 0:
            print(f"Skipping empty file: {url}")
            return 0, 0
        
        with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8') as f:
            packages_data = f.read()
        
        if not packages_data.strip():
            print(f"Skipping zero-byte or unreadable file: {url}")
            return 0, 0
    except requests.RequestException as e:
        print(f"Skipping due to download error: {url} - {e}")
        return 0, 0
    
    packages = packages_data.strip().split("\n\n")
    total_packages = 0
    total_size = 0
    
    for pkg in packages:
        total_packages += 1
        for line in pkg.split("\n"):
            if line.startswith("Size: "):
                total_size += int(line.split("Size: ")[1])
    
    return total_packages, total_size

# Function to process a Sources.gz file
def process_sources_gz(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        if len(response.content) == 0:
            print(f"Skipping empty file: {url}")
            return 0, 0
        
        with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8') as f:
            sources_data = f.read()
        
        if not sources_data.strip():
            print(f"Skipping zero-byte or unreadable file: {url}")
            return 0, 0
    except requests.RequestException as e:
        print(f"Skipping due to download error: {url} - {e}")
        return 0, 0
    
    sources = sources_data.strip().split("\n\n")
    total_projects = 0
    total_source_size = 0
    
    for src in sources:
        total_projects += 1
        in_files_section = False
        
        for line in src.split("\n"):
            if line.startswith("Files:"):
                in_files_section = True
                continue
            if in_files_section and line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    total_source_size += int(parts[1])
            elif in_files_section and not line.strip():
                break  # End of the Files section
    
    return total_projects, total_source_size

# Read the index file
with open(args.index_file, "r") as f:
    index_data = json.load(f)

repo_size_data = {}

for entry in index_data:
    suite = entry['release']
    component = entry['component']
    architecture = entry['architecture']
    index_url = entry['index_url']
    
    print(f"Processing: {index_url}")
    
    if architecture == "source":
        projects, size = process_sources_gz(index_url)
        repo_size_data.setdefault(suite, {}).setdefault(component, {}).setdefault("source", {
            "projects": 0,
            "source_size": 0
        })
        repo_size_data[suite][component]["source"]["projects"] += projects
        repo_size_data[suite][component]["source"]["source_size"] += size
    else:
        packages, size = process_packages_gz(index_url)
        repo_size_data.setdefault(suite, {}).setdefault(component, {}).setdefault(architecture, {
            "packages": 0,
            "total_size": 0
        })
        repo_size_data[suite][component][architecture]["packages"] += packages
        repo_size_data[suite][component][architecture]["total_size"] += size

# Save the result to file
with open(args.output, "w") as f:
    json.dump(repo_size_data, f, indent=2)

print(f"Repository size data saved to {args.output}")

