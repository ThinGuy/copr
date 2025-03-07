## **Sizer**
### **Purpose**  
The **Sizer** script calculates the total size of packages and source files within each suite, component, and architecture.

### **Key Functions**
- Reads `Packages.gz` and `Sources.gz` files.
- Counts:
  - **Total number of packages** for each suite/component/architecture.
  - **Total size of binary packages**.
  - **Total number of source projects**.
  - **Total size of source files** (summed from `.orig.tar.gz`, `.debian.tar.gz`, `.dsc`).
- Outputs repository size statistics.

### **Output**
- JSON with total counts and sizes per suite/component/architecture:
  ```json
  {
    "focal-security": {
      "main": {
        "binary-amd64": {
          "packages": 5000,
          "total_size": 10_000_000_000
        },
        "source": {
          "projects": 1500,
          "source_size": 20_000_000_000
        }
      }
    }
  }
  ```

### **Usage**
```bash
python sizer.py -i ubuntu_indexes.json -o repo_sizes.json
```
