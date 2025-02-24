import aiohttp
import asyncio
import json
import re
from tqdm import tqdm
from aiohttp import ClientSession
from rich.console import Console
from rich.table import Table
import argparse

# Define the base URLs
binary_base_url = "https://changelogs.ubuntu.com/changelogs/binary/"
pool_base_url = "https://changelogs.ubuntu.com/changelogs/pool/"

console = Console()

def get_mode():
    parser = argparse.ArgumentParser(description="Choose mode for fetching package metadata.")
    parser.add_argument("mode", choices=["binary", "pool"], help="Select mode: 'binary' for alphanumeric processing or 'pool' for Ubuntu component processing.")
    args = parser.parse_args()
    return args.mode

async def fetch_dirs(session, base_url):
    async with session.get(base_url) as response:
        if response.status != 200:
            print(f"Failed to fetch {base_url}")
            return []
        html = await response.text()
        return [d for d in re.findall(r'href="([^"/]+)/"', html) if d not in ["changelogs"]]

async def fetch_package_list(session, base_url, component, retries=3):
    component_url = f"{base_url}{component}/"
    for attempt in range(retries):
        try:
            async with session.get(component_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch {component_url}, status {response.status}")
                return await response.text()
        except Exception as e:
            print(f"Attempt {attempt+1} failed for {component_url}: {e}")
            await asyncio.sleep(2 ** attempt)
    print(f"Failed to fetch {component_url} after {retries} attempts")
    return None

async def parse_package_list(session, html, base_url, component):
    package_versions = {}
    package_matches = re.findall(r'href="([^"/]+)/"', html)
    
    for package in package_matches:
        package_versions[package] = []
        package_url = f"{base_url}{component}/{package}/"
        
        async with session.get(package_url) as response:
            if response.status != 200:
                continue
            sub_html = await response.text()
            version_matches = re.findall(r'href="([^"/]+)/"', sub_html)
            for version in version_matches:
                corrected_url = f"{package_url}{version}/"
                copyright_url = f"{corrected_url}copyright"
                changelog_url = f"{corrected_url}changelog"
                package_versions[package].append({"version": version, "copyright_url": copyright_url, "changelog_url": changelog_url})
    
    return package_versions

async def process_component(session, base_url, component, semaphore):
    async with semaphore:
        html = await fetch_package_list(session, base_url, component)
        if not html:
            return {}
        return await parse_package_list(session, html, base_url, component)

async def build_json(mode):
    async with ClientSession() as session:
        base_url = binary_base_url if mode == "binary" else pool_base_url
        components = sorted(await fetch_dirs(session, base_url))
        total_components = len(components)
        semaphore = asyncio.Semaphore(10)
        tasks = {component: process_component(session, base_url, component, semaphore) for component in components}
        
        results = {}
        directory_table = Table(show_header=False, show_lines=False)
        directory_table.add_column("Components", justify="left")
        for comp_name in components:
            directory_table.add_row(comp_name)
        console.print(directory_table)
        
        for component, future in zip(tasks.keys(), asyncio.as_completed(tasks.values())):
            try:
                results[component] = await future
                if results[component]:
                    with open(f"{component}.json", "w") as json_file:
                        json.dump(results[component], json_file, indent=4)
                    console.print(f"[bold green]{component} completed[/bold green]")
            except Exception as e:
                print(f"Error processing {component}: {e}")
        
        print("Processing complete.")

mode = get_mode()
asyncio.run(build_json(mode))
