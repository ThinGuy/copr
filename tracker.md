## **Tracker**
### **Purpose**  
The **Tracker** script analyzes package changes over time, comparing the initial General Availability (GA) release to update repositories.

### **Key Functions**
- Loads `Packages.gz` from GA and `-updates` pockets.
- Tracks:
  - **Version bumps** (newer versions of existing packages).
  - **New packages** introduced in updates.
  - **Removed packages** no longer in updates.
  - **Dependency changes**.
- Helps analyze repository evolution over time.

### **Output**
- JSON report summarizing changes:
  ```json
  {
    "focal": {
      "main": {
        "binary-amd64": {
          "new_packages": ["newlib"],
          "removed_packages": ["oldlib"],
          "updated_packages": {
            "bash": {
              "old_version": "5.0-6ubuntu1",
              "new_version": "5.0-6ubuntu1.2"
            }
          }
        }
      }
    }
  }
  ```

### **Usage**
```bash
python tracker.py -i ubuntu_indexes.json -o repo_changes.json
```
