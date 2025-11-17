# ZenCube - Quick Size Management Reference

## 🎯 Current Size: 21 MB ✅

---

## ⚡ Quick Commands

### Check Size
```bash
du -sh .
```

### Clean Up Now
```bash
./cleanup.sh
```

### Setup Virtual Environment
```bash
./setup.sh
```

### Run GUI
```bash
source venv/bin/activate
python zencube/zencube_modern_gui.py
```

---

## 🛡️ Automatic Protection

✅ **Git Hook** — Auto-cleans before every commit  
✅ **Signal Handlers** — Tests clean up after themselves  
✅ **.gitignore** — Blocks venv and large files  

---

## 📊 Size Breakdown

| Component | Size | In Git? |
|-----------|------|---------|
| Source code | ~20 MB | ✅ Yes |
| venv (minimal) | ~800 MB | ❌ No |
| venv (full ML) | ~8 GB | ❌ No |
| test_output.dat | Auto-removed | ❌ No |

---

## 🆘 Troubleshooting

**Size increased?**
```bash
./cleanup.sh
```

**Can't run GUI?**
```bash
./setup.sh
```

**Before sharing/committing?**
```bash
du -sh .  # Should be ~20 MB
```

---

## 📝 Files Added for Size Management

- `cleanup.sh` — Manual cleanup
- `setup.sh` — Recreate venv
- `.git/hooks/pre-commit` — Auto-cleanup
- `SIZE_MANAGEMENT.md` — Full docs

---

✅ **Project stays at ~20 MB permanently!**
