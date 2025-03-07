#!/usr/bin/env python3
# Ubuntu Repository Tracker
# Revision: 1.0.3

import json
import argparse

def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def compare_repos(ga_file, updates_file, output_file):
    ga_data = load_json(ga_file)
    updates_data = load_json(updates_file)
    
    report = {}
    
    for release, components in ga_data.items():
        if release not in updates_data:
            continue
        report[release] = {}
        
        for component, arches in components.items():
            if component not in updates_data[release]:
                continue
            report[release][component] = {}
            
            for arch, ga_info in arches.items():
                if arch not in updates_data[release][component]:
                    continue
                
                updates_info = updates_data[release][component][arch]
                
                new_packages = set(updates_info.get("packages", [])) - set(ga_info.get("packages", []))
                removed_packages = set(ga_info.get("packages", [])) - set(updates_info.get("packages", []))
                
                version_changes = {}
                for pkg, ver in updates_info.get("versions", {}).items():
                    if pkg in ga_info.get("versions", {}) and ga_info["versions"][pkg] != ver:
                        version_changes[pkg] = {
                            "old": ga_info["versions"][pkg],
                            "new": ver
                        }
                
                report[release][component][arch] = {
                    "new_packages": list(new_packages),
                    "removed_packages": list(removed_packages),
                    "version_changes": version_changes
                }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Comparison report saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compare GA and Updates repo states')
    parser.add_argument('-g', '--ga', required=True, help='Path to GA JSON file')
    parser.add_argument('-u', '--updates', required=True, help='Path to Updates JSON file')
    parser.add_argument('-o', '--output', default='repo_growth_report.json', help='Output report JSON file')
    
    args = parser.parse_args()
    compare_repos(args.ga, args.updates, args.output)

