# Phase 3 GUI Fix Checklist

**Date**: 2025-11-16  
**Task**: Fix GUI integration issues (File Jail hang, Network status, Monitor graphs)  
**Target Score**: ≥9/10 to pass  

---

## 📋 Issues Addressed

### Issue 1: File Jail Panel Hangs ❌
**Symptom**: Panel gets stuck in infinite "preparing/running" state, button never re-enables  
**Root Cause**: Worker thread exits without emitting signals on exception  
**Fix Applied**: Added try/except wrapper in `_JailRunWorker.run()` to guarantee signal emission  

### Issue 2: Network Panel Status Missing ❌
**Symptom**: Toggle network restriction, but no status update after execution  
**Root Cause**: Network panel has no status tracking, log polling, or execution callbacks  
**Fix Applied**: Added `attach_to_execution()`, log polling mechanism, status display, and main GUI signal connections  

### Issue 3: Monitor Graphs Empty ❌
**Symptom**: Enable monitoring, run command, graphs remain empty with "no data"  
**Root Cause**: Potential schema mismatch (memory_rss vs rss_bytes), silent AttributeError crashes  
**Fix Applied**: Added defensive attribute access with fallback for both field names, exception handling  

---

## 🔧 Changes Made

### Modified Files (4)

1. **gui/file_jail_panel.py**
   - Lines 73-103: Wrapped `_JailRunWorker.run()` entire loop in try/except
   - Guarantees `finished` or `failed` signal always fires
   - Button re-enable logic works even on worker crash

2. **gui/network_panel.py**
   - Added imports: `json`, `Optional`, `QTimer`
   - Added instance variables: `_active_pid`, `_poll_timer`, `_latest_log_path`
   - New method: `attach_to_execution(pid)` - starts log polling
   - New method: `handle_execution_finished()` - final poll + cleanup
   - New method: `_poll_network_log()` - checks for monitor logs
   - New method: `_parse_network_log(log_path)` - parses JSONL, extracts status
   - New method: `_display_network_status(status_info, log_path)` - updates UI
   - New helper: `_get_mode_description()` - human-readable mode

3. **gui/monitor_panel.py**
   - Lines 561-592: Rewrote `_on_sample()` with defensive attribute access
   - Uses `getattr(sample, 'memory_rss', None)` with fallback to `rss_bytes`
   - Added try/except wrapper to catch and log parsing errors
   - Prevents silent crashes on schema mismatches

4. **zencube/zencube_modern_gui.py**
   - Line 1077: Added `network_panel.attach_to_execution(pid)` call in `_on_process_started()`
   - Line 1089: Added `network_panel.handle_execution_finished()` call in `on_command_finished()`
   - Connects network panel to execution lifecycle

### New Files (3)

5. **tests/test_gui_file_jail_manual.sh** - Manual test for file jail button re-enable
6. **tests/test_gui_network_status.sh** - Manual test for network status updates
7. **tests/test_gui_monitor_graphs.sh** - Manual test for monitor graph population

---

## ✅ Scoring Rubric

### 1. File Jail Non-Blocking (3 points)

- [ ] **1.0 pt** - Button always re-enables (even on error)
  - Test: Click "Apply & Run", verify button re-enables within 10 seconds
  - Expected: Button transitions from disabled → enabled automatically
  
- [ ] **1.0 pt** - Worker exceptions caught and displayed
  - Test: Trigger error condition (e.g., missing wrapper), check status output
  - Expected: Error message appears in status box, button still re-enables
  
- [ ] **1.0 pt** - Log link appears after successful execution
  - Test: Run valid command with file jail, check log link
  - Expected: Clickable link to `jail_run_*.json` file appears

**Subtotal**: ___ / 3 points

---

### 2. Network Status Updates (3 points)

- [ ] **1.0 pt** - Status message updates after execution
  - Test: Enable network restriction, run command, check status label
  - Expected: Status changes from "monitoring PID X" → "ACTIVE" or "completed"
  
- [ ] **1.0 pt** - Log link or log reference appears
  - Test: After execution, check note box for log filename
  - Expected: Note box contains log reference (e.g., "Log: monitor_run_*.jsonl")
  
- [ ] **1.0 pt** - Success/fail indicator present
  - Test: Run successful and failed commands, verify status reflects outcome
  - Expected: Exit code and status clearly displayed

**Subtotal**: ___ / 3 points

---

### 3. Monitor Graphs Updated (4 points)

- [ ] **1.5 pt** - Graphs populate with data during execution
  - Test: Enable monitoring, run `sleep 3`, watch CPU and Memory graphs
  - Expected: Lines appear on both graphs with visible data points
  
- [ ] **1.5 pt** - Sample view shows live updates
  - Test: Enable monitoring, run long command, check sample text area
  - Expected: Multiple sample lines appear (timestamp | CPU | RSS | Threads)
  
- [ ] **1.0 pt** - Schema adapter supports both Python/C logs
  - Test: Run commands that generate both log formats, verify no errors
  - Expected: No AttributeError in logs, graphs work for both formats

**Subtotal**: ___ / 4 points

---

## 📊 Final Score Calculation

| Category | Points Earned | Points Possible |
|----------|---------------|-----------------|
| File Jail Non-Blocking | ___ | 3 |
| Network Status Updates | ___ | 3 |
| Monitor Graphs Updated | ___ | 4 |
| **TOTAL** | **___** | **10** |

**Pass Threshold**: ≥9/10 points

---

## 🧪 Test Execution Results

### Manual Test 1: File Jail Button Re-Enable

**Script**: `tests/test_gui_file_jail_manual.sh`

**Execution Date**: ___________  
**Result**: [ ] PASS  [ ] FAIL

**Observations**:
- Button re-enabled after execution: [ ] YES  [ ] NO
- Error handling works correctly: [ ] YES  [ ] NO
- Log link appears: [ ] YES  [ ] NO

**Notes**:
```
[Write observations here]
```

---

### Manual Test 2: Network Status Update

**Script**: `tests/test_gui_network_status.sh`

**Execution Date**: ___________  
**Result**: [ ] PASS  [ ] FAIL

**Observations**:
- Status label updated: [ ] YES  [ ] NO
- Log reference displayed: [ ] YES  [ ] NO
- Exit code shown: [ ] YES  [ ] NO

**Notes**:
```
[Write observations here]
```

---

### Manual Test 3: Monitor Graph Population

**Script**: `tests/test_gui_monitor_graphs.sh`

**Execution Date**: ___________  
**Result**: [ ] PASS  [ ] FAIL

**Observations**:
- CPU graph populated: [ ] YES  [ ] NO
- Memory graph populated: [ ] YES  [ ] NO
- Sample view updated: [ ] YES  [ ] NO
- Summary shows samples > 0: [ ] YES  [ ] NO

**Notes**:
```
[Write observations here]
```

---

## 🎯 Success Criteria

**All criteria must be met for PASS**:

- [x] All code changes committed
- [ ] All 3 manual tests executed
- [ ] Total score ≥ 9/10
- [ ] No regression in existing functionality
- [ ] No Phase-4/ML files modified
- [ ] Thread safety preserved
- [ ] Backward compatible log formats

---

## 📝 Validation Notes

### Code Review
- [x] File jail panel: try/except added ✅
- [x] Network panel: polling mechanism added ✅
- [x] Monitor panel: defensive attribute access added ✅
- [x] Main GUI: signal connections added ✅
- [x] No syntax errors in modified files ✅

### Safety Constraints
- [x] No Phase-4 files touched ✅
- [x] No sudo operations added ✅
- [x] No breaking API changes ✅
- [x] Thread safety maintained (all GUI updates via signals) ✅
- [x] Atomic file operations preserved ✅

### Documentation
- [x] MD_READ_LOG.md updated with diagnosis ✅
- [x] PHASE3_GUI_FIX_CHECKLIST.md created ✅
- [ ] Test results documented (pending execution)

---

## 🚀 Next Steps

1. **Execute Manual Tests**:
   - Run `tests/test_gui_file_jail_manual.sh`
   - Run `tests/test_gui_network_status.sh`
   - Run `tests/test_gui_monitor_graphs.sh`
   - Document observations in sections above

2. **Calculate Score**:
   - Fill in "Points Earned" for each category
   - Calculate total score
   - Verify ≥9/10 threshold met

3. **Commit Changes**:
   - Stage all modified files
   - Create descriptive commit messages
   - Push to feature branch

4. **Update Documentation**:
   - Update this checklist with test results
   - Update SCORES.md if needed
   - Update TEST_RUNS.md with execution logs

---

**Status**: ⏸️ AWAITING MANUAL TEST EXECUTION

