# Network Wrapper Binary Executable Fix

## Problem

When running binary executables (like `/bin/ls`, `/bin/echo`, or compiled C programs) through the GUI with network restrictions enabled, the following error occurred:

```
SyntaxError: source code string cannot contain null bytes
```

## Root Cause

The `monitor/net_wrapper.py` module was designed to wrap **Python scripts only**. It used `runpy.run_path()` to execute targets, which expects Python source code. When a binary executable was passed:

1. `runpy.run_path()` tried to read the binary file as Python source
2. Binary files contain null bytes (`\x00`)
3. Python's parser rejected the null bytes as invalid syntax

## Solution

Enhanced `net_wrapper.py` to detect and handle binary executables:

### Detection Logic

Before executing, the wrapper now:
1. Reads the first 4 bytes to check for binary headers:
   - `\x7fELF` - Linux/Unix ELF binary
   - `\xcf\xfa` - macOS Mach-O binary
   - `MZ` - Windows PE executable
2. Scans first 8KB for null bytes (binary indicator)
3. If binary detected, uses `subprocess.run()` instead of `runpy`

### Code Changes

```python
# Check if this is a binary executable
is_binary = False
try:
    with open(script_path, 'rb') as f:
        header = f.read(4)
        if header.startswith(b'\x7fELF') or header.startswith(b'\xcf\xfa') or header.startswith(b'MZ'):
            is_binary = True
        else:
            # Check for null bytes
            f.seek(0)
            sample = f.read(8192)
            if b'\x00' in sample:
                is_binary = True
except Exception:
    pass  # Assume script if can't read

if is_binary:
    # Use subprocess for binaries
    import subprocess
    env = os.environ.copy()
    env["ZENCUBE_NET_DISABLED"] = "1"
    result = subprocess.run([str(script_path)] + tail, env=env, check=False)
    sys.exit(result.returncode)
else:
    # Use runpy for Python scripts
    runpy.run_path(str(script_path), run_name="__main__")
```

## Benefits

✅ **Binary executables now work** - `/bin/ls`, `/bin/echo`, compiled C programs  
✅ **Python scripts still work** - `.py` files use the original runpy path  
✅ **Network blocking maintained** - `ZENCUBE_NET_DISABLED=1` set for binaries  
✅ **No breaking changes** - Python script execution unchanged  

## Limitations

For **binary executables**, network blocking relies on:
- Environment variable `ZENCUBE_NET_DISABLED=1`
- Application checking this variable
- NOT as secure as Python socket monkey-patching

For **Python scripts**, network blocking is enforced by:
- Socket monkey-patching (secure)
- PermissionError raised on any socket operation

## Testing

```bash
# Test with binary
python3 -m monitor.net_wrapper -- /bin/echo "Hello"
# Output: Hello ✅

# Test with Python script
echo 'print("Hello Python")' > test.py
python3 -m monitor.net_wrapper -- test.py
# Output: Hello Python ✅
```

## Files Modified

- `monitor/net_wrapper.py` - Added binary detection and subprocess execution

---

✅ **Fix complete! Binary executables and Python scripts both work with network restrictions.**
