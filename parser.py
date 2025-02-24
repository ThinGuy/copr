import os
import re
import json
import multiprocessing
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

def find_copyright_files(base_dir):
    """Recursively search for 'copyright' files in the given directory."""
    copyright_files = []
    for root, _, files in os.walk(base_dir):
        if "copyright" in files:
            copyright_files.append(os.path.join(root, "copyright"))
    print(f"Found {len(copyright_files)} copyright files in {base_dir}.")
    return copyright_files

def fetch_online_copyrights_list(section_url):
    """Fetch the list of copyright file URLs from the given section URL."""
    try:
        response = requests.get(section_url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return [
                section_url + '/' + a['href'] + '/copyright' 
                for a in soup.find_all('a', href=True) if '/' in a['href']
            ]
        else:
            print(f"Failed to fetch {section_url}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching {section_url}: {e}")
    return []

def fetch_online_copyright(url):
    """Fetch copyright file from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to fetch {url}: HTTP {response.status_code}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def extract_licenses(content, license_pattern):
    """Extract license information from copyright content."""
    licenses = set()
    for line in content.splitlines():
        match = license_pattern.search(line)
        if match:
            for key, value in match.groupdict().items():
                if value:
                    licenses.add(value.strip())
    return licenses

def process_section(section, search_dir, license_pattern, online=False):
    """Process a specific section in parallel and save results to JSON."""
    section_dir = os.path.join(search_dir, "pool", section)
    copyright_files = find_copyright_files(section_dir) if not online else []
    license_data = []
    
    if online:
        base_url = f"http://changelogs.ubuntu.com/changelogs/pool/{section}"
        online_copyright_urls = fetch_online_copyrights_list(base_url)
    else:
        online_copyright_urls = []
    
    for file_path in copyright_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        extracted_licenses = extract_licenses(content, license_pattern)
        
        parent_dir = os.path.basename(os.path.dirname(file_path))
        package_info = parent_dir.split("_")
        if len(package_info) >= 2:
            package_name = package_info[0]
            version = "_".join(package_info[1:])
        else:
            package_name, version = parent_dir, "unknown"
        
        license_data.append({
            "package": package_name,
            "version": version,
            "copyright_url": file_path,
            "licenses": list(extracted_licenses)
        })
    
    for url in online_copyright_urls:
        content = fetch_online_copyright(url)
        if content:
            extracted_licenses = extract_licenses(content, license_pattern)
            package_info = os.path.basename(os.path.dirname(url)).split("_")
            if len(package_info) >= 2:
                package_name = package_info[0]
                version = "_".join(package_info[1:])
            else:
                package_name, version = "unknown", "unknown"
            
            license_data.append({
                "package": package_name,
                "version": version,
                "copyright_url": url,
                "licenses": list(extracted_licenses)
            })
    
    json_output_file = f"{section}_licenses.json"
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(license_data, f, indent=4)
    print(f"Saved {json_output_file} with {len(license_data)} entries.")

def main(search_dir="~/changelogs.ubuntu.com/changelogs", online=False):
    search_dir = os.path.expanduser(search_dir)
    license_pattern = re.compile(
        r'(?P<spdx>SPDX-License-Identifier:.*)|'
        r'(?P<bsd>(4-?clause )?"?BSD"? licen[sc]es?)|'
        r'(?P<boost>(Boost Software|mozilla (public)?|MIT) Licen[sc]es?)|'
        r'(?P<other>(CCPL|BSD|L?GPL)-[0-9a-z.+-]+( Licenses?)?)|'
        r'(?P<cc>Creative Commons( Licenses?)?)|'
        r'(?P<pd>Public Domain( Licenses?)?)',
        re.IGNORECASE
    )
    
    sections = ["main", "universe", "multiverse", "restricted"]
    processes = []
    
    for section in sections:
        p = multiprocessing.Process(target=process_section, args=(section, search_dir, license_pattern, online))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print("Processing complete for all sections.")

if __name__ == "__main__":
    main(online=True)
