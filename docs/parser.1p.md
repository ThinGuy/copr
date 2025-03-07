## **Parser**
### **Purpose**  
The **Parser** script processes the `Packages.gz` and `Sources.gz` files listed in `ubuntu_indexes.json` to extract structured package and source metadata.

### **Key Functions**
- Reads `ubuntu_indexes.json` to determine package sources.
- Downloads and decompresses `Packages.gz` and `Sources.gz`.
- Extracts:
  - **Binary package information** (name, version, architecture, size, dependencies).
  - **Source package information** (name, version, binary packages built from it, size of source files).
- Outputs structured JSON data for use in reports.

### **Output**
- JSON with package metadata, including:
  ```json
  {
    "focal-security": {
      "main": {
        "binary-amd64": [
          {
            "package": "bash",
            "version": "5.0-6ubuntu1.1",
            "size": 123456,
            "dependencies": ["libc6", "ncurses"]
          }
        ],
        "source": [
          {
            "package": "bash",
            "version": "5.0-6ubuntu1.1",
            "source_files": [
              {"filename": "bash_5.0.orig.tar.gz", "size": 2500000}
            ]
          }
        ]
      }
    }
  }
  ```

### **Usage**
```bash
python parser.py -i ubuntu_indexes.json -o parsed_packages.json
```
