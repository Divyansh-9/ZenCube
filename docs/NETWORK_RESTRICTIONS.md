# Network Restrictions – Phase 3 Task B

ZenCube now provides opt-in network isolation for sandboxed workloads. The
implementation favours dev-safe defaults (no root, no persistent firewall
changes) while still exposing a path to full seccomp enforcement when
privileged.

## Overview

- **`--no-net` flag**: the native `zencube/sandbox` binary accepts a
  `--no-net` switch. When available, it installs a seccomp filter that blocks
  `socket`, `connect`, `sendto`, `sendmsg`, `recvfrom`, and `recvmsg`, returning
  `EPERM` to the target process.
- **Python fallback**: when seccomp is unavailable (e.g., unprivileged
  development environments), `monitor/net_wrapper.py` wraps Python commands,
  monkey-patching the `socket` module to raise `PermissionError` and logging
  every attempt to `monitor/logs/net_restrict_*.json`.
- **GUI toggle**: the modern PySide6 GUI features a “Disable Network Access”
  checkbox (with optional enforce mode). Dev-safe mode automatically wraps the
  command with the Python shim; enforce mode instructs the user to run the
  equivalent `sudo sandbox --no-net ...` invocation manually.
- **Namespace helper**: `scripts/disable_network_dev.sh` demonstrates running
  commands inside a temporary network namespace via `unshare`, without touching
  global iptables rules.

## Usage

### Seccomp (Enforce Mode)

```bash
# Build the sandbox if needed
make -C zencube sandbox

# Run a program with network syscalls blocked via seccomp
sudo ./zencube/sandbox --no-net /usr/bin/python3 -c "import socket; socket.socket()"
# -> Permission denied (EPERM)
```

### Dev-Safe Wrapper (No Root)

```bash
python3 -m monitor.net_wrapper -- python3 examples/no_net_probe.py
# Any socket attempt raises PermissionError and is logged to monitor/logs/

./zencube/sandbox --no-net \
    python3 -m monitor.net_wrapper -- python3 examples/no_net_probe.py
# Works even when seccomp cannot be installed (wrapper blocks sockets first).
```

### Optional Namespace Helper

```bash
./scripts/disable_network_dev.sh python3 examples/no_net_probe.py
# Runs inside an ephemeral network namespace; loopback is optionally enabled.
```

## Logging

`monitor/net_wrapper.py` records every blocked attempt in JSON:

```json
{
  "timestamp": "20251112T163000Z",
  "command": ["python3", "examples/no_net_probe.py"],
  "events": [
    {
      "api": "socket.socket",
      "args": ["<AddressFamily.AF_INET: 2>", "<SocketKind.SOCK_STREAM: 1>", "0"],
      "stack": ["..."]
    }
  ],
  "exit_code": 1
}
```

These artefacts live in `monitor/logs/net_restrict_*.json` and are referenced by
Phase 3 test entries.

## Limitations

- Seccomp enforcement requires Linux with `PR_SET_NO_NEW_PRIVS` and `SECCOMP`.
  If those calls fail the sandbox logs a warning and proceeds without the
  filter; the GUI automatically falls back to the Python wrapper.
- The wrapper only applies to Python workloads. Non-Python binaries must rely
  on seccomp (root) or the optional `unshare` script.
- Namespace isolation uses `unshare --net`; this may require extra capabilities
  or a user namespace friendly kernel.

## Related Artefacts

- `zencube/sandbox.c` – `--no-net` flag and seccomp filter
- `monitor/net_wrapper.py` – dev-safe network shim + logging
- `gui/network_panel.py` & `zencube/zencube_modern_gui.py` – GUI integration
- `tests/test_network_restrict.sh` – automated regression test
- `scripts/disable_network_dev.sh` – optional namespace helper
- `monitor/logs/net_restrict_*.json` – audit trail collector
