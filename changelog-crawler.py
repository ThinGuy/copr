#!/usr/bin/env python3
"""
changelog_crawler_v1.0.py
Version: 1.0

This script crawls the Ubuntu changelog repository directories under:
  https://changelogs.ubuntu.com/changelogs/pool/

It recursively searches the four main components (main, universe, multiverse, restricted)
for files named "copyright" and "changelog". From each package directory, it extracts:
  - package name
  - version (extracted from the directory name after the underscore)
  - copyright_url (full URL to the copyright file)
  - changelog_url (full URL to the changelog file)

The collected data is written to packages.json.
  
Usage:
    python3 changelog_crawler_v1.0.py
"""

import asyncio
import aiohttp
import time
import os
import urllib.parse
from bs4 import BeautifulSoup
import json

# Global state for tracking visited URLs and package data.
visited = set()
packages = {}  # key: unique package identifier, value: package info dictionary
hits_count = 0

# Limit concurrent HTTP requests.
semaphore = asyncio.Semaphore(10)

def update_package(url, file_type):
    """
    Update package info in the global packages dictionary based on the URL.
    Expected URL structure:
      /changelogs/changelogs/pool/<component>/<alphanum>/<package>/<package>_<version>/<file>
    """
    parsed = urllib.parse.urlparse(url)
    parts = parsed.path.split('/')
    try:
        pool_index = parts.index("pool")
    except ValueError:
        return

    if len(parts) < pool_index + 6:
        return

    component = parts[pool_index + 1]
    alphanum = parts[pool_index + 2]
    package_name = parts[pool_index + 3]
    package_version_dir = parts[pool_index + 4]
    if "_" in package_version_dir:
        split_res = package_version_dir.split('_', 1)
        version = split_res[1] if len(split_res) == 2 else ""
    else:
        version = ""
    
    key = f"{component}/{alphanum}/{package_name}/{package_version_dir}"
    if key not in packages:
        packages[key] = {
            "package": package_name,
            "version": version,
            "copyright_url": None,
            "changelog_url": None
        }
    if file_type == "copyright":
        packages[key]["copyright_url"] = url
    elif file_type == "changelog":
        packages[key]["changelog_url"] = url

async def crawl(url, session, allowed_base):
    global hits_count
    if not url.endswith('/'):
        url += '/'
    if not url.startswith(allowed_base):
        return
    if url in visited:
        return
    visited.add(url)
    
    async with semaphore:
        try:
            start = time.monotonic()
            async with session.get(url) as response:
                hits_count += 1
                if response.status != 200:
                    print(f"Skipping {url}: status code {response.status}")
                    return
                text = await response.text()
            elapsed = time.monotonic() - start
            print(f"Fetched {url} in {elapsed:.2f} seconds")
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return

    soup = BeautifulSoup(text, "html.parser")
    tasks = []
    for a in soup.find_all("a"):
        href = a.get("href")
        if not href:
            continue
        # Skip Parent Directory link
        if a.text.strip() == "Parent Directory":
            continue
        full_url = urllib.parse.urljoin(url, href)
        if not full_url.startswith(allowed_base):
            continue
        if href.endswith("/"):
            tasks.append(crawl(full_url, session, allowed_base))
        else:
            filename = os.path.basename(urllib.parse.urlparse(full_url).path).lower()
            if filename in ("copyright", "changelog"):
                update_package(full_url, filename)
                print(f"Found {filename}: {full_url}")
    if tasks:
        await asyncio.gather(*tasks)

async def main():
    base_components = [
        "https://changelogs.ubuntu.com/changelogs/pool/main/",
        "https://changelogs.ubuntu.com/changelogs/pool/universe/",
        "https://changelogs.ubuntu.com/changelogs/pool/multiverse/",
        "https://changelogs.ubuntu.com/changelogs/pool/restricted/"
    ]
    async with aiohttp.ClientSession() as session:
        tasks = [crawl(base, session, base) for base in base_components]
        await asyncio.gather(*tasks)
    print("\nCrawling complete.")
    print(f"Total HTTP hits: {hits_count}")
    result = list(packages.values())
    # Write output to packages.json
    with open("packages.json", "w") as f:
        json.dump(result, f, indent=2)
    print("Output written to packages.json")

if __name__ == '__main__':
    asyncio.run(main())

