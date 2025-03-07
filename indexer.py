#!/usr/bin/env python3
# Ubuntu Repository Indexer
# Revision: 1.0.3

import requests
import json
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import argparse

ARCHIVE_URLS = [
    "https://archive.ubuntu.com/ubuntu",
    "https://ports.ubuntu.com/ubuntu-ports",
    "https://esm.ubuntu.com/apps/ubuntu",
    "https://esm.ubuntu.com/cc/ubuntu",
    "https://esm.ubuntu.com/cis/ubuntu",
    "https://esm.ubuntu.com/fips/ubuntu",
    "https://esm.ubuntu.com/fips-preview/ubuntu",
    "https://esm.ubuntu.com/fips-updates/ubuntu",
    "https://esm.ubuntu.com/infra/ubuntu",
    "https://esm.ubuntu.com/infra-legacy/ubuntu",
    "https://esm.ubuntu.com/realtime/ubuntu",
    "https://esm.ubuntu.com/ros/ubuntu",
    "https://esm.ubuntu.com/ros-updates/ubuntu",
    "https://esm.ubuntu.com/usg/ubuntu",
    "https://archive.anbox-cloud.io/stable"
]

headers = {'User-Agent': 'Ubuntu-Indexer/1.0'}

parser = argparse.ArgumentParser(description='Ubuntu repository indexer')
parser.add_argument('-o', '--output', default='ubuntu_indexes.json', help='Output JSON filename')
args = parser.parse_args()

# Fetch available releases (suites) from archive
def get_available_releases():
    response = requests.get("https://archive.ubuntu.com/ubuntu/dists/", headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    releases = [a['href'].strip('/') for a in soup.find_all('a', href=True)
                if not a['href'].startswith(('..', 'devel'))]
    return releases

# Fetch available architectures dynamically
def get_available_architectures(archive_url, suite, component):
    comp_url = f"{archive_url}/dists/{suite}/{component}/"
    response = requests.get(comp_url, headers=headers)
    if response.status_code != 200:
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    architectures = [a['href'].strip('/') for a in soup.find_all('a', href=True)
                     if a['href'].startswith('binary-') or a['href'].startswith('source')]
    return architectures

releases = get_available_releases()
index_urls = []

for archive_url in ARCHIVE_URLS:
    for release in releases:
        for component in ["main", "universe", "multiverse", "restricted"]:
            suite_url = f"{archive_url}/dists/{release}/{component}/"
            response = requests.get(suite_url, headers=headers)
            if response.status_code != 200:
                continue
            architectures = get_available_architectures(archive_url, release, component)
            for arch in architectures:
                index_file = "Packages.gz" if arch != "source" else "Sources.gz"
                index_url = f"{suite_url}{arch}/{index_file}"
                print(f"Adding: {index_url}")
                index_urls.append({
                    "archive_url": archive_url,
                    "release": release,
                    "component": component,
                    "architecture": arch,
                    "index_url": index_url
                })

with open(args.output, "w") as f:
    json.dump(index_urls, f, indent=2)

print(f"Index URLs saved to {args.output}")

