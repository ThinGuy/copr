import os
import re
import json
import multiprocessing
from collections import defaultdict

def find_copyright_files(base_dir):
    """Recursively search for 'copyright' files in the given directory."""
    copyright_files = []
    for root, _, files in os.walk(base_dir):
        if "copyright" in files:
            copyright_files.append(os.path.join(root, "copyright"))
    print(f"Found {len(copyright_files)} copyright files in {base_dir}.")
    return copyright_files

def extract_licenses(file_path, license_pattern):
    """Extract license information from a copyright file."""
    licenses = set()
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = license_pattern.search(line)
                if match:
                    for key, value in match.groupdict().items():
                        if value:
                            licenses.add(value.strip())
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    print(f"Processed {file_path}, found {len(licenses)} licenses.")
    return licenses

def process_section(section, search_dir, license_pattern):
    """Process a specific section in parallel and save results to JSON."""
    section_dir = os.path.join(search_dir, "pool", section)
    copyright_files = find_copyright_files(section_dir)
    license_data = []
    
    for file_path in copyright_files:
        extracted_licenses = extract_licenses(file_path, license_pattern)
        
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
    
    json_output_file = f"{section}_licenses.json"
    with open(json_output_file, "w", encoding="utf-8") as f:
        json.dump(license_data, f, indent=4)
    print(f"Saved {json_output_file} with {len(license_data)} entries.")

def main(search_dir="~/changelogs.ubuntu.com/changelogs"):
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
        p = multiprocessing.Process(target=process_section, args=(section, search_dir, license_pattern))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
    
    print("Processing complete for all sections.")

if __name__ == "__main__":
    main()
