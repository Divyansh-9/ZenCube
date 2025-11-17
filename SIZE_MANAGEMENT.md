# ZenCube Size Management Guide

## 🎯 Target Project Size: 20-50 MB (without venv)

The ZenCube project is designed to stay under 100 MB in the repository, with virtual environments managed separately.

---

## 📊 Current State

- **Repository size:** ~20 MB
- **With venv:** ~800 MB (not in repo)
- **With full ML venv:** ~8 GB (not in repo)

---

## 🗑️ Auto-Cleanup System

### Automatic Cleanup (Git Hook)

The project has a **pre-commit git hook** that automatically removes bloat before commits:

- ✅ Virtual environments (venv, .venv)
- ✅ Large test files (test_output.dat, *.dat > 10MB)
- ✅ Python cache (__pycache__, *.pyc)

**This runs automatically** when you commit, ensuring the repo stays clean.

---

## 🧹 Manual Cleanup

### Quick Cleanup Command

```bash
./cleanup.sh
```

This script:
- Removes all virtual environments
- Deletes test output files
- Clears Python cache
- Shows before/after size

**Run this anytime** to ensure project is under 50 MB.

---

## 🔒 Prevention (.gitignore)

The `.gitignore` file prevents large files from being tracked:

```gitignore
# Virtual environments
venv/
.venv/
env/
ENV/

# Large test files
*.dat
test_output.*

# Build artifacts
build/
dist/
*.so
*.o

# Python cache
__pycache__/
*.pyc
```

---

## ⚠️ Common Bloat Sources

### 1. Virtual Environments (700 MB - 8 GB)

**Problem:** venv directories contain all installed packages.

**Solution:**
- ✅ Always in `.gitignore`
- ✅ Auto-removed by git hook
- ✅ Recreate with `./setup.sh`

### 2. test_output.dat (Variable, up to 14 GB!)

**Problem:** Created by `file_size_test` when testing file limits.

**Solution:**
- ✅ Now auto-removed by signal handlers in the test
- ✅ Pattern `*.dat` in `.gitignore`
- ✅ Auto-removed by git hook

### 3. Python Cache (10-100 MB)

**Problem:** `__pycache__` directories accumulate.

**Solution:**
- ✅ In `.gitignore`
- ✅ Removed by cleanup script
- ✅ Auto-cleaned by git hook

---

## 🚀 Best Practices

### Before Committing

```bash
# Option 1: Let git hook auto-clean (recommended)
git commit -m "your message"

# Option 2: Manual cleanup first
./cleanup.sh
git add .
git commit -m "your message"
```

### Before Sharing/Archiving

```bash
# Full cleanup
./cleanup.sh

# Verify size
du -sh .

# Should show ~20-50 MB
```

### After Cloning

```bash
# Setup environment
./setup.sh

# This creates venv and installs deps
# venv will be ignored by git
```

---

## 📝 Size Verification Commands

```bash
# Check current size
du -sh .

# Check specific directories
du -sh venv .venv test_output.dat 2>/dev/null

# Find large files (> 10 MB)
find . -type f -size +10M -exec du -h {} \;

# File count
find . -type f | wc -l
```

---

## 🔧 Emergency Cleanup

If project size exceeds 100 MB:

```bash
# 1. Check what's taking space
du -ah . | sort -hr | head -n 20

# 2. Run full cleanup
./cleanup.sh

# 3. Remove specific large files
rm -f test_output.dat
rm -rf venv .venv

# 4. Clear all cache
find . -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# 5. Verify
du -sh .
```

---

## 📦 What's Intentionally Kept

These files are part of the project and should stay:

- **Git metadata (.git/):** ~6 MB
- **ML model artifacts (models/):** ~2.6 MB (trained LSTM)
- **Monitoring logs (monitor/logs/):** ~3 MB
- **Source code:** ~6 MB
- **Documentation:** ~2 MB

Total: **~20 MB**

---

## ⚙️ Size Management Files

| File | Purpose |
|------|---------|
| `cleanup.sh` | Manual cleanup script |
| `.git/hooks/pre-commit` | Auto-cleanup before commits |
| `.gitignore` | Prevent large files from tracking |
| `requirements-minimal.txt` | Lightweight deps (~800 MB) |
| `requirements.txt` | Full deps (~8 GB with ML) |
| `setup.sh` | Recreate venv easily |

---

## 🎯 Size Targets

| State | Size | Description |
|-------|------|-------------|
| **Repository** | 20-50 MB | Source code only |
| **With minimal venv** | ~800 MB | GUI dependencies |
| **With full ML venv** | ~8 GB | torch + CUDA |
| **During testing** | Variable | Temporary test files auto-cleaned |

---

## ✅ Checklist: Keep Project Small

- [x] Virtual environments in `.gitignore`
- [x] Auto-cleanup git hook installed
- [x] Manual cleanup script available
- [x] Test files auto-remove themselves
- [x] Large patterns in `.gitignore`
- [x] Easy venv recreation (`./setup.sh`)
- [x] Size verification commands documented

---

## 💡 Pro Tips

1. **Run cleanup before long-term storage:**
   ```bash
   ./cleanup.sh && tar -czf zencube-backup.tar.gz .
   ```

2. **Check size regularly:**
   ```bash
   du -sh .
   ```

3. **Never commit venv** - It's huge and machine-specific

4. **Test file cleanup** - `file_size_test` now has signal handlers

5. **Use git hook** - It auto-cleans before every commit

---

## 🆘 Troubleshooting

### "Project is 15 GB again!"

```bash
# This happens when test_output.dat is created
# Quick fix:
./cleanup.sh

# Permanent fix: Already applied
# - Signal handlers in file_size_test.c
# - Git hook auto-cleanup
# - .gitignore patterns
```

### "Can't run GUI after cleanup"

```bash
# Venv was removed (intentionally)
# Recreate it:
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
```

### "Git won't commit"

```bash
# Pre-commit hook might be running cleanup
# This is normal! Just wait for it to finish
# Then commit again
```

---

**✅ With this system, ZenCube will stay at ~20 MB permanently!**
