# Task A – Test Runs

| Timestamp (UTC) | Command | Result Summary |
|----------------|---------|----------------|
| 2025-11-12T03:57:19Z | `./tests/test_jail_dev.sh` | PASS – wrapper returned 2 and log captured `/etc/hosts` violation |
| 2025-11-12T16:04:20Z | `./tests/test_gui_file_jail_py.sh` | PASS – PySide6 panel prepared jail and logged run via jail_wrapper |
