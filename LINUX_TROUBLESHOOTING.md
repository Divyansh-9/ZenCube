# Linux Troubleshooting Guide - ZenCube GUI

## 🐧 Common Issue: "No directory ./sandbox"

If you're getting a "sandbox not found" error on Linux, follow this guide to fix it.

---

## 🔍 Quick Diagnosis

### Check Current Location
```bash
pwd
# Should show: /path/to/ZenCube/zencube
```

### Check if Sandbox Exists
```bash
ls -la sandbox
# Should show: -rwxr-xr-x ... sandbox
```

---

## ✅ Solution 1: Run from Correct Directory

### Problem
You're running the GUI from the wrong directory.

### Fix
```bash
# Navigate to the zencube directory
cd /path/to/ZenCube/zencube

# Run the GUI
python3 Zencube_gui.py
```

---

## ✅ Solution 2: Build the Sandbox

### Problem
Sandbox binary doesn't exist yet.

### Fix
```bash
cd /path/to/ZenCube/zencube

# Build the sandbox
make

# Verify it was created
ls -la sandbox

# Should show:
# -rwxr-xr-x 1 user user 12345 Oct 13 sandbox

# Run GUI
python3 Zencube_gui.py
```

---

## ✅ Solution 3: Make Sandbox Executable

### Problem
Sandbox exists but isn't executable.

### Fix
```bash
cd /path/to/ZenCube/zencube

# Make it executable
chmod +x sandbox

# Verify permissions
ls -la sandbox
# Should show: -rwxr-xr-x (note the 'x' for executable)

# Run GUI
python3 Zencube_gui.py
```

---

## ✅ Solution 4: Use Settings Dialog

### Problem
Sandbox is in a different location.

### Fix
1. Launch GUI: `python3 Zencube_gui.py`
2. Click **⚙️ Settings** button
3. Browse or type the full path to your sandbox binary
4. Click **Apply**

---

## 📊 GUI Auto-Detection

The GUI v1.3 now searches these locations automatically:

```python
1. ./sandbox                          # Current directory
2. /path/to/script/sandbox            # Same dir as GUI script
3. ./zencube/sandbox                  # Subdirectory
4. ../sandbox                         # Parent directory
5. /usr/local/bin/sandbox             # System install
6. ~/zencube/sandbox                  # User home
```

---

## 🧪 Testing the Fix

### Step 1: Check GUI Terminal Output

When you launch the GUI, look for these messages:

**Success**:
```
🧊 ZenCube Sandbox Terminal
================================================================================
Ready to execute commands. Select a file and configure limits.

✅ Sandbox found: ./sandbox
```

**Warning**:
```
⚠️ WARNING: Sandbox binary not found!
   Looking for: ./sandbox
   Current directory: /home/user/some/path

💡 To fix this:
   1. Make sure you're in the correct directory
   2. Build the sandbox: cd zencube && make
   3. Or run GUI from zencube directory: cd zencube && python Zencube_gui.py
```

---

### Step 2: Verify in Settings

1. Click **⚙️ Settings**
2. Check the "Current Status" section:
   ```
   Path: /home/user/ZenCube/zencube/sandbox
   Exists: ✅ Yes
   Executable: ✅ Yes
   Working Dir: /home/user/ZenCube/zencube
   ```

---

## 🎯 Recommended Setup (Linux)

### Project Structure
```
ZenCube/
├── zencube/
│   ├── sandbox          ← Executable binary
│   ├── sandbox.c
│   ├── Makefile
│   ├── Zencube_gui.py   ← GUI script
│   └── tests/
│       ├── infinite_loop
│       ├── memory_hog
│       └── ...
```

### Running the GUI
```bash
# Always run from the zencube directory
cd ZenCube/zencube
python3 Zencube_gui.py
```

### Building from Scratch
```bash
# Clone repo
git clone https://github.com/KamalSDhami/ZenCube.git
cd ZenCube/zencube

# Build sandbox
make

# Verify
ls -la sandbox
# Should show: -rwxr-xr-x ... sandbox

# Run GUI
python3 Zencube_gui.py
```

---

## ⚙️ Using WSL Checkbox on Linux

### Important for Linux Users

When running on Linux, **UNCHECK the WSL box**:

```
☐ Use WSL (Windows Subsystem for Linux)
   (Auto-detected: Linux/Unix)
```

**Why?**
- WSL is only for Windows users
- On Linux, you want **native execution**
- GUI auto-detects this, but you can toggle manually

**Status Bar Should Show:**
```
Ready | OS: Linux | Native Mode | Sandbox: ./sandbox
```

---

## 🔧 Advanced: Custom Sandbox Location

### System-Wide Install

```bash
# Build sandbox
cd ZenCube/zencube
make

# Install to system
sudo cp sandbox /usr/local/bin/

# Update GUI settings
# In Settings dialog, set path to: /usr/local/bin/sandbox
```

### User-Specific Install

```bash
# Create directory
mkdir -p ~/bin

# Copy sandbox
cp ZenCube/zencube/sandbox ~/bin/

# Make executable
chmod +x ~/bin/sandbox

# Update GUI settings
# In Settings dialog, set path to: ~/bin/sandbox
```

---

## 🚨 Error Messages Explained

### "No such file or directory"
```
[Sandbox] Child Error: Failed to execute './sandbox': No such file or directory
```

**Cause**: Sandbox binary not found  
**Fix**: Build sandbox with `make`, ensure you're in correct directory

---

### "Permission denied"
```
[Sandbox] Child Error: Failed to execute './sandbox': Permission denied
```

**Cause**: Sandbox exists but isn't executable  
**Fix**: Run `chmod +x sandbox`

---

### "command not found: wsl"
```
wsl: command not found
```

**Cause**: WSL checkbox is enabled on Linux  
**Fix**: Uncheck **Use WSL** checkbox in GUI

---

## 📝 Complete Example Session

```bash
# Start fresh
cd ~
git clone https://github.com/KamalSDhami/ZenCube.git
cd ZenCube/zencube

# Build
make clean
make

# Verify
ls -la sandbox
# Output: -rwxr-xr-x 1 user user 23456 Oct 13 18:30 sandbox

# Check we're in right place
pwd
# Output: /home/user/ZenCube/zencube

# Install Python dependencies (if needed)
pip3 install tkinter  # Usually pre-installed

# Run GUI
python3 Zencube_gui.py

# In GUI:
# 1. Verify terminal shows: ✅ Sandbox found: ./sandbox
# 2. Verify status bar shows: OS: Linux | Native Mode
# 3. Verify WSL checkbox is UNCHECKED
# 4. Click "infinite_loop" quick command
# 5. Enable CPU limit: 3 seconds
# 6. Click Execute
# 7. Should work! ✅
```

---

## 🆘 Still Having Issues?

### Debug Checklist

- [ ] I'm in the `zencube` directory (`pwd` shows correct path)
- [ ] Sandbox binary exists (`ls sandbox` works)
- [ ] Sandbox is executable (`ls -la sandbox` shows `-rwxr-xr-x`)
- [ ] GUI terminal shows `✅ Sandbox found`
- [ ] WSL checkbox is UNCHECKED (Linux/Unix mode)
- [ ] Status bar shows "Native Mode"
- [ ] I can run sandbox manually: `./sandbox /bin/ls`

### Manual Test

```bash
# Test sandbox directly
cd ZenCube/zencube
./sandbox --cpu=3 ./tests/infinite_loop

# Should output:
# [Sandbox] CPU limit set to: 3 seconds
# [Sandbox] Starting sandbox process...
# Starting infinite loop...
# ... (then killed after 3 seconds)
```

If manual test works but GUI doesn't, check:
1. GUI Settings dialog for correct path
2. Working directory in GUI terminal output
3. Any error messages in GUI terminal

---

## 💡 Pro Tips

### 1. **Always Use Absolute Paths**
Instead of `./sandbox`, use `/full/path/to/sandbox` in Settings

### 2. **Create Shell Script**
```bash
#!/bin/bash
# ~/run-zencube-gui.sh
cd ~/ZenCube/zencube
python3 Zencube_gui.py
```

Make executable: `chmod +x ~/run-zencube-gui.sh`  
Run anytime: `~/run-zencube-gui.sh`

### 3. **Add to PATH**
```bash
# Add to ~/.bashrc or ~/.bash_profile
export PATH="$HOME/ZenCube/zencube:$PATH"

# Reload
source ~/.bashrc

# Now you can run from anywhere:
Zencube_gui.py
```

---

## 📚 Related Documentation

- [GUI_USAGE.md](../GUI_USAGE.md) - Complete GUI guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [README.md](README.md) - Full project documentation
- [CROSS_PLATFORM_SUPPORT.md](../CROSS_PLATFORM_SUPPORT.md) - WSL toggle feature

---

**Last Updated**: October 13, 2025  
**GUI Version**: v1.3  
**Status**: Linux Support Enhanced ✅
