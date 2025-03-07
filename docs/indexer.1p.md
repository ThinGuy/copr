## **Indexer**
### **Purpose**  
The **Indexer** script crawls Ubuntu and Ubuntu Pro/ESM repositories to generate a structured list of package index URLs.

### **Key Functions**
- Fetches **suites** (release + pockets) from various Ubuntu archive locations.
- Identifies **components** (main, universe, multiverse, restricted, or main for Pro/ESM).
- Detects **architectures**, including binaries (`binary-*`) and sources (`source`).
- Generates URLs for `Packages.gz` and `Sources.gz` files dynamically.
- Stores the output in **`ubuntu_indexes.json`** for downstream processing.

### **Output**
- JSON file containing structured repository index data:
  ```json
  [
    {
      "suite": "focal-security",
      "component": "main",
      "architecture": "binary-amd64",
      "index_url": "https://archive.ubuntu.com/ubuntu/dists/focal-security/main/binary-amd64/Packages.gz"
    },
    {
      "suite": "focal-security",
      "component": "main",
      "architecture": "source",
      "index_url": "https://archive.ubuntu.com/ubuntu/dists/focal-security/main/source/Sources.gz"
    }
  ]
  ```

### **Usage**
```bash
python indexer.py -o ubuntu_indexes.json
```
