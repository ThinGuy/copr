import argparse
import requests
import re
import apt
import os
import time

# List of lib? exceptions that use full "lib?" prefix
LIB_EXCEPTIONS = {
    "lib+", "lib0", "lib2", "lib3", "lib4", "lib6", "liba", "libb", "libc", "libd", "libe",
    "libf", "libg", "libh", "libi", "libj", "libk", "libl", "libm", "libn", "libo", "libp",
    "libq", "libr", "libs", "libt", "libu", "libv", "libw", "libx", "liby", "libz"
}
COMPONENTS = ["main", "universe", "multiverse", "restricted"]

def determine_first_letter(package_name):
    """Determine the first letter path segment based on package naming rules."""
    if package_name.startswith("lib") and any(package_name.startswith(prefix) for prefix in LIB_EXCEPTIONS):
        return package_name[:4]  # Use "lib?" prefix
    return package_name[0]  # Use just the first letter

def find_package_component(package_name, package_version):
    """Find the correct component by checking each possible URL in the pool method."""
    first_letter = determine_first_letter(package_name)
    base_url = "https://changelogs.ubuntu.com/changelogs/pool"

    for component in COMPONENTS:
        url = f"{base_url}/{component}/{first_letter}/{package_name}/{package_name}_{package_version}/copyright"
        response = requests.head(url)
        if response.status_code == 200:
            return component, url
    return None, None

def extract_spdx_license(copyright_url):
    """Fetch and extract the SPDX license ID from the copyright file."""
    try:
        response = requests.get(copyright_url, timeout=5)
        if response.status_code == 200:
            matches = re.findall(r"License:\s*(\S+)", response.text)
            return list(set(matches)) if matches else ["Unknown"]
    except requests.RequestException:
        pass
    return ["Unknown"]

def get_urls(package_name, package_version, method):
    """Generate URLs based on the selected method (pool or binary)."""
    first_letter = determine_first_letter(package_name)
    results = {}

    if method == "pool":
        component, pool_base_url = find_package_component(package_name, package_version)
        copyright_url = f"{pool_base_url}" if component else "Not found"
        changelog_url = f"{pool_base_url.rsplit('/', 1)[0]}/changelog" if component else "Not found"
    else:  # Binary method
        binary_base_url = f"https://changelogs.ubuntu.com/changelogs/binary/{first_letter}/{package_name}/{package_version}"
        copyright_url = f"{binary_base_url}/copyright"
        changelog_url = f"{binary_base_url}/changelog"
        component = "N/A (binary method)"

    licenses = extract_spdx_license(copyright_url) if copyright_url != "Not found" else ["Unknown"]

    return {
        "component": component if component else "Unknown",
        "copyright_url": copyright_url,
        "changelog_url": changelog_url,
        "licenses": licenses
    }

def get_package_info(package_name, package_version=None):
    """Use python-apt to determine available Ubuntu releases and architectures for a package."""
    cache = apt.Cache()
    releases = []
    architectures = set()

    try:
        pkg = cache[package_name]
        for version in pkg.versions:
            if package_version and version.version != package_version:
                continue
            releases.append(version.origin)
            for arch in version.architectures:
                architectures.add(arch)

        if not package_version:
            package_version = pkg.versions[0].version  # Use the latest version if not provided

    except KeyError:
        return package_version, ["Package not found"], ["Unknown"]

    return package_version, list(set(releases)) if releases else ["Version not found"], sorted(architectures) if architectures else ["Unknown"]

def process_manifest(file_path_or_url, method, include_release_arch, output_file=None):
    """Process a Debian manifest file from a local file or URL and generate package info."""
    results = []
    
    # Handle URLs
    if file_path_or_url.startswith("http"):
        response = requests.get(file_path_or_url)
        if response.status_code != 200:
            print(f"Error: Unable to fetch manifest from {file_path_or_url}")
            return
        lines = response.text.splitlines()
    else:
        # Read local file
        if not os.path.exists(file_path_or_url):
            print(f"Error: File {file_path_or_url} not found.")
            return
        with open(file_path_or_url, "r", encoding="utf-8") as file:
            lines = file.readlines()

    total_packages = len(lines)
    processed_count = 0
    start_time = time.time()

    for line in lines:
        line = line.strip()
        
        # Ignore snap packages
        if line.startswith("snap:"):
            continue
        
        # Parse package name and version
        parts = line.split("\t")
        if len(parts) != 2:
            continue  # Skip malformed lines
        
        package_name, package_version = parts
        
        # Generate URLs
        package_data = get_urls(package_name, package_version, method)
        
        # Get Ubuntu releases and architectures if requested
        if include_release_arch:
            package_version, releases, architectures = get_package_info(package_name, package_version)
            package_data["releases"] = ", ".join(releases)
            package_data["architectures"] = ", ".join(architectures)

        results.append({
            "package": package_name,
            "version": package_version,
            **package_data
        })

        processed_count += 1
        elapsed_time = time.time() - start_time
        print(f"Processed {processed_count}/{total_packages} packages in {elapsed_time:.2f} seconds...", end="\r")

    print("\nProcessing complete!")
    print_results(results, output_file)

def print_results(results, output_file):
    """Prints results and optionally saves to a file."""
    for res in results:
        print(f"Package: {res['package']} (Version: {res['version']})")
        print(f"Component: {res['component']}")
        print(f"Copyright URL: {res['copyright_url']}")
        print(f"Changelog URL: {res['changelog_url']}")
        print(f"SPDX Licenses: {', '.join(res['licenses'])}")
        if "releases" in res:
            print(f"Ubuntu Releases: {res['releases']}")
            print(f"Supported Architectures: {res['architectures']}")
        print("\n" + "-"*60 + "\n")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as f:
            for res in results:
                f.write(f"{res['package']}\t{res['version']}\t{res['component']}\t"
                        f"{res['copyright_url']}\t{res['changelog_url']}\t"
                        f"{', '.join(res['licenses'])}\n")
        print(f"Results saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Fetch Ubuntu package copyright and SPDX info.")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--manifest", help="Path to local manifest file or URL.")
    input_group.add_argument("--package", help="Single package name (latest version will be used).")
    input_group.add_argument("--package-version", nargs=2, metavar=("PACKAGE", "VERSION"), help="Specific package name and version.")

    method_group = parser.add_mutually_exclusive_group(required=True)
    method_group.add_argument("--pool", action="store_true", help="Use pool method URLs.")
    method_group.add_argument("--binary", action="store_true", help="Use binary method URLs.")

    parser.add_argument("--no-release-arch", action="store_true", help="Skip release and architecture data.")
    parser.add_argument("--output", help="Optional output file to save results.")

    args = parser.parse_args()

    method = "pool" if args.pool else "binary"
    include_release_arch = not args.no_release_arch

    if args.manifest:
        process_manifest(args.manifest, method, include_release_arch, args.output)

if __name__ == "__main__":
    main()
