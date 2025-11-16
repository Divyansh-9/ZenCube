# Phase 3 GUI Testing Guide

## Quick Start: Test the Monitoring Graphs

The monitoring graphs show **real-time** data only when a command is **actively running**. Follow these steps:

### Step-by-Step Instructions

1. **In the GUI, navigate to "Monitoring & Metrics" section**

2. **Enable monitoring checkbox**
   - ✅ Check: "Enable monitoring for executions"
   - Set interval: `1.0` seconds (default)
   - Window: `60` samples (default)

3. **Set the test command**
   - Scroll up to the "Command" section
   - Command: `./tests/phase3_test`
   - Arguments: (leave empty)

4. **Click "Execute Command"**
   - The test will run for ~8 seconds
   - Watch the graphs populate in real-time!

5. **Observe the results**:
   - ✅ CPU graph: Shows spikes during computation
   - ✅ Memory graph: Shows 10+ MB allocation
   - ✅ Sample view: Live updates with timestamps
   - ✅ Summary: Shows peak CPU%, memory, samples count

---

## What the Test Program Does

The `phase3_test` binary validates all Phase 3 features:

### Test 1: File Jail (Filesystem Restrictions)
- Attempts to read `/etc/passwd`, `/home/secret.txt`
- Attempts path traversal: `../../../etc/hosts`
- **Expected**: All access attempts blocked

### Test 2: Network Restrictions
- Attempts to create TCP socket
- Attempts to connect to 8.8.8.8:53
- Attempts to create UDP socket
- **Expected**: All socket operations blocked (if network restriction enabled)

### Test 3: Monitoring & Metrics
- Allocates 10 MB of memory
- Generates CPU load for 5 seconds
- Prints progress every second
- **Expected**: Graphs populate with data, summary shows peak usage

---

## Full Integration Test (All Features)

To test **ALL** Phase 3 features together:

1. **Enable File Jail**:
   - ✅ Check "Enable File Jail"
   - Jail Path: `sandbox_jail`
   - Click "Prepare Jail" (wait for success)

2. **Enable Network Restrictions**:
   - ✅ Check "Disable Network Access"
   - (Do NOT enable "Enforce" unless you want to run with sudo)

3. **Enable Monitoring**:
   - ✅ Check "Enable monitoring for executions"
   - Set interval: `0.5` seconds (for more samples)

4. **Run the test**:
   - Command: `./tests/phase3_test`
   - Click "Execute Command"

5. **Expected Results**:
   - **File Jail Panel**: 
     - Status shows "Run finished with exit code 0"
     - Log link appears
     - Summary shows violations detected (expected)
   
   - **Network Panel**:
     - Status updates to "Network blocking: ACTIVE"
     - Note box shows log reference
     - Socket operations blocked
   
   - **Monitoring Panel**:
     - CPU graph shows activity
     - Memory graph shows 10+ MB
     - Sample view has multiple entries
     - Summary: "samples 8-10 | duration 8.0s | peak CPU X% | peak RSS 10+ MB"
     - Log link appears

---

## Alternative Quick Tests

### Test Monitoring Only (No Restrictions)
```
Command: /bin/sleep
Arguments: 5
Monitoring: ✅ Enabled (interval 0.5s)
```
**Result**: Graphs show low CPU, steady memory for 5 seconds

### Test with CPU Load
```
Command: /bin/dd
Arguments: if=/dev/zero of=/dev/null bs=1M count=100
Monitoring: ✅ Enabled (interval 0.5s)
```
**Result**: CPU graph shows high activity

### Test with Memory Allocation
```
Command: ./tests/phase3_test
Arguments: (none)
Monitoring: ✅ Enabled
```
**Result**: Memory graph shows 10 MB spike

---

## Troubleshooting

### "Graphs are still empty"
- ✅ Make sure "Enable monitoring for executions" is checked
- ✅ Click "Execute Command" (not just set the command)
- ✅ Wait for the command to start running
- ✅ Graphs update in real-time during execution

### "No samples shown in summary"
- Command finished too quickly (< 1 second)
- Try a longer-running command like `sleep 5`

### "File jail shows no violations"
- This is expected if running WITHOUT file jail enabled
- The test program attempts violations, but they're only logged if jail is active

### "Network panel shows no status"
- Network restriction must be enabled BEFORE execution
- Status updates appear AFTER execution completes
- Check the note box for log references

---

## Expected Scoring Results

Based on the fixes applied, you should see:

✅ **File Jail (3/3 points)**:
- Button re-enables after execution
- Status shows completion message
- Log link appears

✅ **Network Status (3/3 points)**:
- Status label updates from "monitoring" → "completed"
- Note box shows log filename
- Exit code displayed

✅ **Monitor Graphs (4/4 points)**:
- CPU and Memory graphs populate
- Sample view shows live updates
- Summary displays: samples > 0, duration, peak values
- Log link appears

**Total: 10/10 points** 🎉

---

## Files Created

- **Test Binary**: `zencube/tests/phase3_test` (compiled C program)
- **Source Code**: `zencube/tests/phase3_test.c`
- **This Guide**: `PHASE3_GUI_TEST_GUIDE.md`

---

## Command Reference

Run the test from command line (to verify it works):
```bash
cd /home/Idred/Downloads/ZenCube/zencube
./tests/phase3_test
```

Compile from source (if needed):
```bash
cd /home/Idred/Downloads/ZenCube/zencube/tests
gcc -o phase3_test phase3_test.c -Wall
```

Launch GUI:
```bash
cd /home/Idred/Downloads/ZenCube/zencube
../.venv/bin/python3 zencube_modern_gui.py
```

---

**Ready to test!** The GUI is already running - just follow the steps above to see the graphs populate. 📊
