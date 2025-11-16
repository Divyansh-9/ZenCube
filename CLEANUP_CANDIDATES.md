# ZenCube Production Cleanup - File Removal Candidates

**Last Updated:** 2025-11-16  
**Purpose:** List of files that can be removed for a clean production deployment

---

## ✅ SAFE TO REMOVE (Total: ~120+ files)

### 📁 **1. Backup Archives (2 directories)**
Complete backups of previous phases - no longer needed:

```bash
backup_phase3_python_core/          # Old Python monitoring code (replaced by core_c/)
backup_phase4_archive/              # Archived ML components (removed in Phase 4)
```

**Size saved:** ~5-10 MB  
**Reason:** Redundant backups, all code is in git history

---

### 📋 **2. Development Documentation & Checklists (47 files)**

#### Root-level docs (26 files):
```
BUGFIX_LAYOUT_ISSUES.md
BUGFIX_LINUX_PATHS.md
BUGFIX_PATH_CONVERSION.md
CROSS_PLATFORM_SUPPORT.md
GUI_IMPLEMENTATION.md
GUI_JSONL_INTEGRATION.md
GUI_USAGE.md
GUI_USER_GUIDE.md
INTEGRATION_COMPLETE.md
LINUX_TROUBLESHOOTING.md
MODERN_GUI_DOCUMENTATION.md
OPTIONAL_IMPROVEMENTS_COMPLETE.md
PHASE3_GUI_TEST_GUIDE.md
PHASE4_RESTORATION_REPORT.md
README_UPDATE_SUMMARY.md
RESPONSIVE_FEATURES.md
```

#### phase3/ directory (10 files):
```
phase3/FINAL_REPORT.md
phase3/INTEGRATION_CHECKLIST.md
phase3/MD_READ_LOG.md
phase3/NOTES.md
phase3/PHASE3_CORE_C_CHECKLIST.md
phase3/PHASE3_CORE_C_COMPLETE.md
phase3/PHASE3_GUI_FIX_CHECKLIST.md
phase3/PHASE3_MASTER_CHECKLIST.md
phase3/SCORES.md
phase3/TEST_RUNS.md
```

#### zencube/ subdirectory (4 files):
```
zencube/PHASE2_COMPLETE.md
zencube/TEST_RESULTS.md
zencube/TESTING_CHECKLIST.md
```

#### docs/ directory (7 files):
```
docs/GUI_FILE_JAIL.md
docs/MONITORING_DASHBOARD.md
docs/NETWORK_RESTRICTIONS.md
docs/QA_PREPARATION.md
docs/ROLE_1_CORE_SANDBOX.md
docs/ROLE_2_GUI_FRONTEND.md
docs/ROLE_3_INTEGRATION.md
docs/ROLE_4_TESTING.md
```

**Keep these docs:**
- `README.md` (main project README)
- `QUICK_START.md` (user-facing quick start)
- `core_c/README.md` (C-core documentation)
- `zencube/README.md` (sandbox documentation)
- `zencube/QUICKSTART.md` (sandbox quick start)
- `docs/README.md` (docs index)
- `docs/PROJECT_OVERVIEW.md` (high-level overview)

**Reason:** Development notes, internal checklists, and historical bug reports not needed in production

---

### 🧪 **3. Test Scripts & Validation Tools (18 files)**

```
tests/test_alert_engine.sh
tests/test_alerting.sh
tests/test_core_c_prom.sh
tests/test_gui_file_jail.sh
tests/test_gui_file_jail_manual.sh
tests/test_gui_file_jail_py.sh
tests/test_gui_jsonl.py
tests/test_gui_monitor_graphs.sh
tests/test_gui_monitoring_py.sh
tests/test_gui_network_status.sh
tests/test_inference.sh              # ML-related (removed feature)
tests/test_jail_dev.sh
tests/test_jsonl_summary.py
tests/test_log_rotate.sh
tests/test_monitor_daemon.sh
tests/test_network_restrict.sh
tests/test_prom_exporter.sh
tests/test_sampler.sh
```

**Keep these test scripts:**
- `zencube/test_sandbox.sh` (core sandbox tests)
- `zencube/test_phase2.sh` (resource limit tests)

**Reason:** Development/CI test scripts, not needed for runtime

---

### 🤖 **4. Archived ML Components (Removed in Phase 4)**

Complete ML training/inference subsystem (no longer in use):

```
data/
├── collector.py
├── labeler.py
├── sample_generator.py
├── sequences.py
├── dataset_prompt.md
└── __pycache__/

models/
├── train.py
├── evaluate.py
├── artifacts/
│   ├── lstm.pt
│   ├── meta.json
│   └── report.md

inference/
├── ml_inference.py
└── __pycache__/

monitor/ml_guard.py              # ML integration module
```

**Reason:** ML anomaly detection was removed in Phase 4 cleanup (see PHASE4_RESTORATION_REPORT.md)

---

### 📝 **5. Temporary/Backup Files (8 files)**

```
requirements.txt.bak
requirements.txt.pkg_backup
requirements.txt.tmp
phase3_test_verification.txt
phase4_additions.txt
phase4_cleanup_report.txt
phase4_pkgs_candidate.txt
phase4_remove_list.txt
phase4_shared_pkgs.txt
ML_REMOVAL_FINAL_REPORT.txt
zencube_gui.py.broken
gui.log
```

**Reason:** Temporary files from cleanup operations, broken backups, and logs

---

### 🏗️ **6. Build Artifacts (Optional - regenerated on build)**

```
core_c/*.o                    # Object files (6 files)
core_c/bin/                   # Binaries (4 executables)
zencube/*.o                   # Object files
zencube/sandbox               # Binary (can rebuild)
```

**Reason:** These are generated during `make`, not source files

---

### 🐍 **7. Python Cache Directories**

```
data/__pycache__/
inference/__pycache__/
gui/__pycache__/
monitor/__pycache__/
```

**Reason:** Python bytecode cache, auto-regenerated

---

## 📦 **Recommended Production Structure**

After cleanup, keep only these directories:

```
ZenCube/
├── .git/                          # Git history (keep)
├── .github/                       # GitHub config (keep if using Actions)
├── .gitignore                     # Keep
├── README.md                      # User-facing docs
├── QUICK_START.md                 # User quick start
├── requirements.txt               # Python deps for GUI
│
├── core_c/                        # Core C monitoring library
│   ├── *.c, *.h                   # Source files
│   ├── Makefile                   # Build system
│   ├── README.md                  # C-core docs
│   └── bin/                       # Compiled binaries (or remove if distributing source)
│
├── zencube/                       # Sandbox subsystem
│   ├── sandbox.c                  # Main sandbox
│   ├── core.c, core.h             # Core integration
│   ├── Makefile                   # Build system
│   ├── README.md                  # Sandbox docs
│   ├── QUICKSTART.md              # Sandbox quick start
│   └── tests/                     # Test programs (memory_hog, etc.)
│       ├── *.c                    # Test source files
│       └── phase3_test            # Integration test binary
│
├── monitor/                       # Python monitoring utilities
│   ├── __init__.py
│   ├── jail_wrapper.py            # Development jail wrapper
│   ├── net_wrapper.py             # Network restriction wrapper
│   ├── resource_monitor.py        # Legacy Python monitor (optional)
│   ├── alert_manager.py           # Alert system
│   ├── prometheus_exporter.py     # Metrics export
│   ├── log_rotate.py              # Log rotation
│   └── logs/                      # Runtime logs directory
│
├── gui/                           # PySide6 GUI
│   ├── __init__.py
│   ├── _mpl_canvas.py             # Matplotlib integration
│   ├── file_jail_panel.py         # File jail UI
│   ├── monitor_panel.py           # Monitoring UI
│   └── network_panel.py           # Network restriction UI
│
├── scripts/                       # Build/setup scripts
│   ├── build_jail_dev.sh
│   ├── disable_network_dev.sh
│   └── validate_phase3_core_c.sh
│
├── zencube_gui.py                 # Main GUI entry point (legacy)
├── demo_zencube.sh                # Demo script
└── sandbox_jail/                  # Empty jail directory template
```

---

## 🗑️ **Removal Commands**

### Option A: Archive then remove (safer)
```bash
cd /home/Idred/Downloads/ZenCube

# Create archive of everything to be removed
tar -czf zencube_cleanup_archive_$(date +%Y%m%d).tar.gz \
    backup_phase3_python_core/ \
    backup_phase4_archive/ \
    data/ \
    models/ \
    inference/ \
    phase3/*.md \
    tests/*.sh tests/*.py \
    *.md \
    requirements.txt.* \
    phase*.txt \
    *.broken \
    gui.log

# Remove directories
rm -rf backup_phase3_python_core/ backup_phase4_archive/
rm -rf data/ models/ inference/

# Remove documentation
rm -f BUGFIX_*.md CROSS_PLATFORM_SUPPORT.md GUI_*.md
rm -f INTEGRATION_COMPLETE.md LINUX_TROUBLESHOOTING.md
rm -f MODERN_GUI_DOCUMENTATION.md OPTIONAL_IMPROVEMENTS_COMPLETE.md
rm -f PHASE*.md README_UPDATE_SUMMARY.md RESPONSIVE_FEATURES.md
rm -f phase3/*.md
rm -f zencube/PHASE2_COMPLETE.md zencube/TEST_RESULTS.md zencube/TESTING_CHECKLIST.md
rm -f docs/GUI_FILE_JAIL.md docs/MONITORING_DASHBOARD.md docs/NETWORK_RESTRICTIONS.md
rm -f docs/QA_PREPARATION.md docs/ROLE_*.md

# Remove test scripts
rm -f tests/test_*.sh tests/test_*.py

# Remove temp files
rm -f requirements.txt.* phase*.txt *.broken gui.log ML_REMOVAL_FINAL_REPORT.txt

# Remove Python cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null

echo "✅ Cleanup complete! Archive saved."
```

### Option B: Direct removal (faster, no archive)
```bash
cd /home/Idred/Downloads/ZenCube

# Add to .gitignore first (so they don't come back)
cat >> .gitignore << 'EOF'

# Development artifacts
backup_*/
data/
models/
inference/
phase3/*.md
tests/*.sh
tests/*.py
*_REPORT.md
*_CHECKLIST.md
BUGFIX_*.md
GUI_*.md
PHASE*.md
*.bak
*.tmp
*.broken
gui.log
phase*.txt
__pycache__/
*.pyc
EOF

# Then remove
git rm -rf backup_phase3_python_core/ backup_phase4_archive/ data/ models/ inference/
git rm tests/*.sh tests/*.py
git rm phase3/*.md
git rm BUGFIX_*.md GUI_*.md INTEGRATION_COMPLETE.md LINUX_TROUBLESHOOTING.md
git rm MODERN_GUI_DOCUMENTATION.md OPTIONAL_IMPROVEMENTS_COMPLETE.md
git rm PHASE*.md README_UPDATE_SUMMARY.md RESPONSIVE_FEATURES.md
git commit -m "chore: Remove development artifacts and archived components"
```

---

## 📊 **Space Savings Estimate**

| Category | Files | Size |
|----------|-------|------|
| Backup archives | 2 dirs | ~8-12 MB |
| ML components | 3 dirs | ~2-5 MB |
| Documentation | 47 files | ~300 KB |
| Test scripts | 18 files | ~50 KB |
| Temp files | 12 files | ~100 KB |
| **TOTAL** | **~80+ items** | **~10-18 MB** |

---

## ⚠️ **What to KEEP**

### Essential Runtime Files:
- `zencube/sandbox` (or source to rebuild)
- `core_c/bin/*` (sampler, alert_daemon, prom_exporter, logrotate)
- `gui/*.py` (GUI panels)
- `monitor/*.py` (Python monitoring utilities)
- `zencube_gui.py` or `zencube/zencube_modern_gui.py` (GUI entry point)
- `requirements.txt` (Python dependencies)

### Essential Docs:
- `README.md` (project overview)
- `QUICK_START.md` (user guide)
- `core_c/README.md` (C-core docs)
- `zencube/README.md` (sandbox docs)
- `docs/PROJECT_OVERVIEW.md` (architecture)

### Build System:
- All `Makefile` files
- `scripts/*.sh` (build helpers)

---

## 🎯 **Minimal Production Deploy**

For a minimal Docker/production image, you only need:

```
ZenCube/
├── core_c/bin/          # Pre-built binaries
├── zencube/sandbox      # Pre-built sandbox
├── gui/                 # GUI source
├── monitor/             # Monitor utilities
├── zencube_gui.py       # GUI entry point
├── requirements.txt     # Python deps
└── README.md            # Docs
```

**Total size:** ~2-3 MB (without .git)

---

## 📝 **Notes**

1. **Git history preserved:** Even after removing files, git history contains all versions
2. **Rebuild from source:** Keep `*.c`, `*.h`, `Makefile` if distributing source code
3. **Virtual environment:** `.venv/` is in `.gitignore` (not tracked, but keep locally)
4. **Logs directory:** `monitor/logs/` is runtime-generated, keep directory structure

---

## ✅ **Validation**

After cleanup, verify core functionality:

```bash
# Build sandbox
cd zencube && make clean all

# Build core_c
cd ../core_c && make clean all

# Test integration
cd ../zencube
./sandbox --enable-core-c --cpu=5 /bin/sleep 2

# Check log created
ls -lh ../monitor/logs/jail_run_*.jsonl

# Test GUI (requires X11/Wayland)
cd ..
.venv/bin/python3 zencube_gui.py
```

If all tests pass, cleanup was successful!
