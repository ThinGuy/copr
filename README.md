# **Ubuntu Project and Package Dashboard Overview**
Need to understand your use of Ubuntu, including free and open source software? The aim of the **Ubuntu Project and Package Dashboard** is to automate the process, provide scalable insights into package availability, repository size, and change history. It's designed to help developers, sysadmins, and security teams make smarter decisions, faster.

## **Purpose**  
The **Ubuntu Project and Package Dashboard** is a comprehensive system designed to track, analyze, and report on Ubuntu package repositories, including standard LTS archives and Ubuntu Pro/ESM repositories. It provides indexing, parsing, sizing, and tracking functionalities to offer detailed insights into repository growth, changes, and package metadata.

## **Key Features**  
**Automated Repository Indexing** – Dynamically discovers all available Ubuntu repositories, suites, components, and architectures.  
**Package & Source Analysis** – Extracts and structures metadata from `Packages.gz` and `Sources.gz` files.  
**Repository Sizing** – Calculates total package and source file sizes per suite, component, and architecture.  
**Change Tracking** – Compares repository states over time, highlighting updates, additions, and removals.  
**Support for Ubuntu Pro/ESM** – Includes security and compliance-focused repositories such as FIPS, USG, and ESM Apps.  
**JSON Output for Easy Integration** – Outputs structured data that can be used for web dashboards, reports, and further analysis.  

---

## **Core Components**  

### **Indexer**
- Scans Ubuntu repositories and identifies `Packages.gz` and `Sources.gz` locations.
- Supports both LTS and Ubuntu Pro/ESM repositories.
- Outputs structured repository data to **`ubuntu_indexes.json`**.

**🔹 Input:** Ubuntu repository URLs  
**🔹 Output:** `ubuntu_indexes.json` (list of package index URLs)  
**🔹 Runs:** Once daily to update repository metadata  

---

### **Parser**
- Extracts metadata from `Packages.gz` (binaries) and `Sources.gz` (source packages).
- Provides structured package information, including dependencies and file sizes.
- Outputs parsed data to **`parsed_packages.json`**.

**🔹 Input:** `ubuntu_indexes.json`  
**🔹 Output:** `parsed_packages.json` (detailed package metadata)  
**🔹 Runs:** After Indexer updates  

---

### **Sizer**
- Calculates the total number and size of packages and source files per suite/component/architecture.
- Tracks both binary and source package sizes, ensuring accurate repository sizing.
- Outputs size reports to **`repo_sizes.json`**.

**🔹 Input:** `ubuntu_indexes.json`  
**🔹 Output:** `repo_sizes.json` (repository size statistics)  
**🔹 Runs:** After Parser updates  

---

### **Tracker**
- Tracks changes in repositories over time, comparing the GA (General Availability) release to updates.
- Identifies version bumps, new package additions, removals, and dependency changes.
- Outputs historical change reports to **`repo_changes.json`**.

**🔹 Input:** `ubuntu_indexes.json`  
**🔹 Output:** `repo_changes.json` (repository evolution report)  
**🔹 Runs:** Periodically to track changes  

---

## **Workflow**
**Indexer** → Finds package lists (`Packages.gz` and `Sources.gz`)  
**Parser** → Extracts package details  
**Sizer** → Calculates repository size  
**Tracker** → Tracks package changes over time  

### **Example Use Case**
A user wants to know how much storage is needed for a specific Ubuntu repository.  
**Sizer** will compute total binary and source package sizes.  

A developer wants to track package updates in Ubuntu 22.04 over time.  
**Tracker** will compare GA to `-updates` and `-security` pockets.  

A security team needs insights into packages available in **Ubuntu Pro/ESM**.  
**Parser** extracts metadata, and **Indexer** ensures Pro repos are covered.  

---

## **Script overview**
| Script  | Purpose | Input | Output |
|---------|---------|-------|--------|
| **Indexer** | Indexes repository URLs and finds `Packages.gz` and `Sources.gz` | Ubuntu repositories | `ubuntu_indexes.json` |
| **Parser** | Extracts package metadata from `Packages.gz` and `Sources.gz` | `ubuntu_indexes.json` | `parsed_packages.json` |
| **Sizer** | Computes repository size statistics | `ubuntu_indexes.json` | `repo_sizes.json` |
| **Tracker** | Tracks package changes over time | `ubuntu_indexes.json` | `repo_changes.json` 

---

## **Future Enhancements**
**Web Dashboard:** Visual representation of repo growth, package trends, and sizes.  
**Interactive Reports:** User-defined queries for sizing and change tracking.  
**API Integration:** Allow other tools to query package data dynamically.  

---

## **Conclusion**  
The Ubuntu Project and Package Dashboard is an automated, scalable platform for the comprehensive monitoring and analysis of Ubuntu repositories. It aggregates and structures critical data points, including package availability, repository footprint, and historical change logs, to facilitate informed decision-making for development, system administration, and security operations.
