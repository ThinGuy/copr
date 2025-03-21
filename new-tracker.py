#!/usr/bin/env python3
# tracker.py v2.0
# Tracks Ubuntu repository growth and generates visualizations for key insights.

import json
import matplotlib.pyplot as plt
import numpy as np
import os
import argparse

# === Load Data ===
def load_data(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data file: {e}")
        return {}

# === Graph: Total Package Counts by Release ===
def plot_total_packages(data, output_dir):
    releases = []
    package_counts = []

    for repo, releases_data in data.items():
        for release, suites in releases_data.items():
            total_pkgs = sum(
                sum(details["packages"] for details in arch_data.values())
                for suite, comp_data in suites.items()
                for arch_data in comp_data.values()
            )
            releases.append(release)
            package_counts.append(total_pkgs)

    plt.figure(figsize=(10, 6))
    plt.bar(releases, package_counts, color='#4CAF50')
    plt.title('Total Package Counts by Ubuntu Release')
    plt.xlabel('Ubuntu Release')
    plt.ylabel('Total Packages')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'total_packages_by_release.png'))
    plt.close()

# === Graph: Repository Growth Trends ===
def plot_growth_trends(data, output_dir):
    pockets = ["release", "updates", "security", "backports", "proposed"]
    sizes = {pocket: [] for pocket in pockets}

    for repo, releases_data in data.items():
        for release, suites in releases_data.items():
            for pocket in pockets:
                pocket_size = sum(
                    sum(details["size"] for details in arch_data.values())
                    for suite, comp_data in suites.items()
                    if pocket in suite
                    for arch_data in comp_data.values()
                )
                sizes[pocket].append(pocket_size)

    x_values = np.arange(len(sizes["release"]))

    plt.figure(figsize=(10, 6))
    for pocket in pockets:
        plt.plot(x_values, sizes[pocket], marker='o', label=pocket)

    plt.title('Repository Growth Trends by Pocket')
    plt.xlabel('Ubuntu Releases')
    plt.ylabel('Total Size (MB)')
    plt.xticks(x_values, list(data.keys()), rotation=45, ha="right")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'growth_trends.png'))
    plt.close()

# === Graph: Top 10 Largest Packages ===
def plot_top10_packages(data, output_dir):
    package_sizes = {}
    
    for repo, releases_data in data.items():
        for release, suites in releases_data.items():
            for suite, comp_data in suites.items():
                for comp, arch_data in comp_data.items():
                    for arch, details in arch_data.items():
                        for pkg in details["packages_details"]:
                            package_sizes[pkg["name"]] = pkg["size"]

    sorted_packages = sorted(package_sizes.items(), key=lambda x: x[1], reverse=True)[:10]

    package_names, package_sizes = zip(*sorted_packages)

    plt.figure(figsize=(10, 6))
    plt.barh(package_names, package_sizes, color='#f0ad4e')
    plt.title('Top 10 Largest Packages')
    plt.xlabel('Size (MB)')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'top10_packages.png'))
    plt.close()

# === Main Program ===
def main():
    parser = argparse.ArgumentParser(description='Track Ubuntu repository growth and visualize key insights.')
    parser.add_argument('-f', '--file', required=True, help='Path to the JSON data file (e.g., ubuntu_reposize.json)')
    parser.add_argument('-o', '--output', required=True, help='Directory to save generated charts')
    
    args = parser.parse_args()

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    data = load_data(args.file)
    if not data:
        print("No valid data found. Exiting...")
        return

    # Generate Charts
    plot_total_packages(data, args.output)
    plot_growth_trends(data, args.output)
    plot_top10_packages(data, args.output)

    print(f"Visualizations saved in: {args.output}")

if __name__ == "__main__":
    main()

