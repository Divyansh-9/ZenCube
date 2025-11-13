# ROLE 4: Testing & Quality Assurance Engineer

## 👤 Your Role

You are responsible for **validation, testing, and security verification** - ensuring ZenCube works correctly and safely. Your expertise is in test design, security testing, exploit development (for testing), and quality assurance.

---

## 📚 What You Need to Know Inside Out

### Your Primary Responsibilities

1. **Test Program Development**: Create programs that test resource limits
2. **Test Execution**: Run comprehensive test suites
3. **Security Validation**: Verify sandbox effectiveness
4. **Attack Simulation**: Develop exploits to test defenses
5. **Documentation**: Record test results and findings

---

## 🧪 Test Suite Overview

### Test Programs Location

```
zencube/tests/
├── infinite_loop.c          # CPU limit test
├── infinite_loop            # Compiled binary
├── memory_hog.c             # Memory limit test
├── memory_hog               # Compiled binary
├── fork_bomb.c              # Process limit test
├── fork_bomb                # Compiled binary
├── file_size_test.c         # File size limit test
└── file_size_test           # Compiled binary
```

### Test Scripts

```
zencube/
├── test_sandbox.sh          # Basic functional tests
├── test_phase2.sh           # Comprehensive Phase 2 tests
└── demo.sh                  # User-friendly demonstrations
```

---

## 🔬 Test Programs Deep Dive

### 1. CPU Limit Test: infinite_loop.c

**Purpose**: Verify that CPU time limits are enforced

#### Source Code Analysis:

```c
#include <stdio.h>
#include <unistd.h>

int main(void) {
    unsigned long long counter = 0;
    
    printf("Starting infinite loop (use Ctrl+C to stop manually)...\n");
    printf("This program is designed to test CPU time limits.\n");
    fflush(stdout);
    
    /* Infinite loop that consumes CPU time */
    while (1) {
        counter++;
        
        /* Print progress every billion iterations */
        if (counter % 1000000000 == 0) {
            printf("Still running... counter: %llu billion\n", 
                   counter / 1000000000);
            fflush(stdout);
        }
    }
    
    /* This should never be reached */
    return 0;
}
```

#### Key Features:

1. **Infinite Loop**: `while(1)` never terminates naturally
2. **CPU Intensive**: Increments counter (pure computation)
3. **Progress Indicator**: Prints every 1 billion iterations
4. **Buffer Flushing**: `fflush()` ensures output is visible immediately

#### Test Execution:

```bash
# Without limits - runs forever (until manually stopped)
./tests/infinite_loop

# With CPU limit - terminates after 5 seconds
./sandbox --cpu=5 ./tests/infinite_loop
```

#### Expected Behavior:

```
Starting infinite loop...
This program is designed to test CPU time limits.
Still running... counter: 1 billion
Still running... counter: 2 billion
Still running... counter: 3 billion
[Sandbox] Process terminated by signal 24 (SIGXCPU)
⚠️  RESOURCE LIMIT VIOLATED: CPU time limit exceeded
```

#### What to Verify:

✅ Process terminates after ~5 seconds (±0.5s tolerance)  
✅ Signal is SIGXCPU (24)  
✅ Sandbox detects and reports CPU limit violation  
✅ Exit code is non-zero (failure)  

---

### 2. Memory Limit Test: memory_hog.c

**Purpose**: Verify memory limits prevent excessive allocation

#### Source Code Analysis:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define CHUNK_SIZE_MB 10

int main(void) {
    size_t chunk_size = CHUNK_SIZE_MB * 1024 * 1024;  /* 10 MB chunks */
    size_t total_allocated = 0;
    int chunk_count = 0;
    char *ptr;
    
    printf("Starting memory allocation test...\n");
    printf("Will allocate memory in %d MB chunks\n", CHUNK_SIZE_MB);
    fflush(stdout);
    
    /* Keep allocating memory until we fail or are killed */
    while (1) {
        ptr = (char *)malloc(chunk_size);
        
        if (ptr == NULL) {
            printf("malloc() failed after allocating %zu MB\n", 
                   total_allocated / (1024 * 1024));
            printf("This is expected when memory limit is enforced\n");
            break;
        }
        
        /* Actually touch the memory to ensure it's allocated */
        memset(ptr, 0, chunk_size);
        
        chunk_count++;
        total_allocated += chunk_size;
        
        printf("Allocated chunk #%d (Total: %zu MB)\n", 
               chunk_count, total_allocated / (1024 * 1024));
        fflush(stdout);
        
        /* Small delay to make output readable */
        usleep(100000);  // 0.1 second
    }
    
    return 0;
}
```

#### Key Features:

1. **Incremental Allocation**: Allocates 10 MB at a time
2. **Memory Touching**: `memset()` ensures physical allocation (not just virtual)
3. **Progress Tracking**: Reports total memory used
4. **Graceful Handling**: Checks if `malloc()` returns NULL

#### Why memset() is Critical:

```c
// WITHOUT memset:
ptr = malloc(1024 * 1024 * 1024);  // Request 1 GB
// OS might not actually allocate (lazy allocation)
// Virtual memory assigned, but no physical RAM used yet

// WITH memset:
ptr = malloc(1024 * 1024 * 1024);
memset(ptr, 0, 1024 * 1024 * 1024);  // Force allocation
// OS MUST allocate physical RAM
// Limit is actually enforced
```

#### Test Execution:

```bash
# Without limits - allocates until system runs out of memory
./tests/memory_hog

# With 256 MB limit
./sandbox --mem=256 ./tests/memory_hog
```

#### Expected Behavior:

**Scenario 1: malloc() Fails**
```
Allocated chunk #1 (Total: 10 MB)
Allocated chunk #2 (Total: 20 MB)
...
Allocated chunk #25 (Total: 250 MB)
malloc() failed after allocating 250 MB
This is expected when memory limit is enforced
```

**Scenario 2: Process Killed**
```
Allocated chunk #1 (Total: 10 MB)
Allocated chunk #2 (Total: 20 MB)
...
Allocated chunk #26 (Total: 260 MB)
[Sandbox] Process terminated by signal 9 (SIGKILL)
⚠️  Process was killed (possibly by memory limit)
```

#### What to Verify:

✅ Process cannot allocate more than 256 MB  
✅ Either malloc() fails or process is killed  
✅ System remains stable (no swap thrashing)  
✅ Total allocation ≤ specified limit  

---

### 3. Process Limit Test: fork_bomb.c

**Purpose**: Verify process count limits prevent fork bombs

#### Source Code Analysis:

```c
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>

int main(void) {
    int fork_count = 0;
    pid_t pid;
    
    printf("Starting controlled fork test...\n");
    printf("⚠️  This tests process limits - DO NOT run without limits!\n");
    fflush(stdout);
    
    /* Attempt to fork multiple times */
    while (1) {
        pid = fork();
        
        if (pid < 0) {
            /* Fork failed - expected when limit is reached */
            printf("fork() failed after %d successful forks: %s\n", 
                   fork_count, strerror(errno));
            printf("This is expected when process limit is enforced.\n");
            fflush(stdout);
            break;
        } else if (pid == 0) {
            /* Child process - just sleep and exit */
            sleep(2);
            exit(0);
        } else {
            /* Parent process */
            fork_count++;
            printf("Successfully created child #%d (PID: %d)\n", 
                   fork_count, pid);
            fflush(stdout);
        }
    }
    
    /* Wait for all children to finish */
    while (wait(NULL) > 0);
    
    printf("Test complete. Created %d child processes.\n", fork_count);
    return 0;
}
```

#### Why This is Safe:

**Real Fork Bomb** (DANGEROUS):
```c
// NEVER RUN THIS WITHOUT LIMITS!
while(1) fork();
// Each child also forks → exponential growth
// 1 → 2 → 4 → 8 → 16 → 32 → 64 → 128 → ...
// System crashes in seconds!
```

**Our Test** (SAFE):
```c
while(1) {
    pid = fork();
    if (pid == 0) {
        sleep(2);  // Child sleeps, doesn't fork
        exit(0);
    }
}
// Only parent forks → linear growth
// Children just sleep and exit
```

#### Test Execution:

```bash
# NEVER run without limits!
# ./tests/fork_bomb  # DON'T DO THIS!

# Safe: With 10 process limit
./sandbox --procs=10 ./tests/fork_bomb
```

#### Expected Behavior:

```
Starting controlled fork test...
⚠️  This tests process limits - DO NOT run without limits!
Successfully created child #1 (PID: 12345)
Successfully created child #2 (PID: 12346)
Successfully created child #3 (PID: 12347)
...
Successfully created child #9 (PID: 12353)
fork() failed after 9 successful forks: Resource temporarily unavailable
This is expected when process limit is enforced.
Test complete. Created 9 child processes.
```

#### What to Verify:

✅ fork() fails after reaching limit  
✅ Error is EAGAIN (Resource temporarily unavailable)  
✅ System remains responsive  
✅ No exponential process growth  
✅ Children properly cleaned up (no zombies)  

---

### 4. File Size Limit Test: file_size_test.c

**Purpose**: Verify file size limits prevent disk exhaustion

#### Source Code Analysis:

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CHUNK_SIZE_MB 10

int main(void) {
    FILE *fp;
    size_t chunk_size = CHUNK_SIZE_MB * 1024 * 1024;
    char *buffer;
    size_t total_written = 0;
    int chunk_count = 0;
    
    printf("Starting file size test...\n");
    printf("Will write data in %d MB chunks\n", CHUNK_SIZE_MB);
    fflush(stdout);
    
    /* Allocate buffer */
    buffer = (char *)malloc(chunk_size);
    if (!buffer) {
        fprintf(stderr, "Failed to allocate buffer\n");
        return 1;
    }
    memset(buffer, 'A', chunk_size);
    
    /* Open file for writing */
    fp = fopen("test_output.dat", "wb");
    if (!fp) {
        fprintf(stderr, "Failed to open file\n");
        free(buffer);
        return 1;
    }
    
    /* Write chunks until we fail */
    while (1) {
        size_t written = fwrite(buffer, 1, chunk_size, fp);
        
        if (written < chunk_size) {
            printf("Write failed after %zu MB\n", 
                   total_written / (1024 * 1024));
            break;
        }
        
        chunk_count++;
        total_written += written;
        
        printf("Wrote chunk #%d (Total: %zu MB)\n", 
               chunk_count, total_written / (1024 * 1024));
        fflush(stdout);
    }
    
    fclose(fp);
    free(buffer);
    return 0;
}
```

#### Test Execution:

```bash
# With 100 MB file size limit
./sandbox --fsize=100 ./tests/file_size_test
```

#### Expected Behavior:

```
Starting file size test...
Will write data in 10 MB chunks
Wrote chunk #1 (Total: 10 MB)
Wrote chunk #2 (Total: 20 MB)
...
Wrote chunk #10 (Total: 100 MB)
[Sandbox] Process terminated by signal 25 (SIGXFSZ)
⚠️  RESOURCE LIMIT VIOLATED: File size limit exceeded
```

#### What to Verify:

✅ Process terminated by SIGXFSZ  
✅ File size ≤ specified limit  
✅ Disk space not exhausted  
✅ File can be deleted after test  

---

## 🧪 Test Scripts

### test_sandbox.sh

**Purpose**: Basic functional testing

```bash
#!/bin/bash

echo "=== ZenCube Sandbox Test Suite ==="
echo

# Test 1: Basic execution
echo "Test 1: Basic execution (no limits)"
./sandbox /bin/echo "Hello, ZenCube!"
echo

# Test 2: CPU limit
echo "Test 2: CPU time limit (5 seconds)"
./sandbox --cpu=5 ./tests/infinite_loop
echo

# Test 3: Memory limit
echo "Test 3: Memory limit (256 MB)"
./sandbox --mem=256 ./tests/memory_hog
echo

# Test 4: Process limit
echo "Test 4: Process limit (10 processes)"
./sandbox --procs=10 ./tests/fork_bomb
echo

# Test 5: File size limit
echo "Test 5: File size limit (100 MB)"
./sandbox --fsize=100 ./tests/file_size_test
echo

echo "=== All tests complete ==="
```

### test_phase2.sh

**Purpose**: Comprehensive Phase 2 validation

More detailed testing with:
- Multiple limit combinations
- Edge cases (limit = 0, very high limits)
- Performance measurements
- Output validation

---

## 🛡️ Security Testing

### Attack Scenarios to Test

#### 1. Fork Bomb Attack

**Objective**: Verify system survives fork bomb attempt

```bash
# Test without limit (DANGEROUS - don't do this!)
# ./tests/fork_bomb

# Test with limit (SAFE)
./sandbox --procs=10 ./tests/fork_bomb

# Verify:
# - fork() fails appropriately
# - System remains responsive
# - No cascading failures
```

#### 2. Memory Exhaustion

**Objective**: Prevent Out-of-Memory (OOM) killer from affecting system

```bash
# Test with various memory limits
./sandbox --mem=100 ./tests/memory_hog
./sandbox --mem=500 ./tests/memory_hog
./sandbox --mem=1024 ./tests/memory_hog

# Verify:
# - Process cannot exceed limit
# - System memory usage stays stable
# - No swap thrashing
# - Other processes unaffected
```

#### 3. CPU Monopolization

**Objective**: Ensure single process can't monopolize CPU

```bash
# Run multiple CPU-intensive tasks
for i in {1..5}; do
    ./sandbox --cpu=10 ./tests/infinite_loop &
done

# Verify:
# - All processes get CPU time
# - System remains responsive
# - Each terminates after 10 seconds
```

#### 4. Disk Space Exhaustion

**Objective**: Prevent disk filling attacks

```bash
# Test with file size limit
./sandbox --fsize=100 ./tests/file_size_test

# Verify:
# - File doesn't exceed limit
# - SIGXFSZ received
# - Disk space remains available
```

---

## 📊 Test Matrix

### Resource Limit Combinations

| Test # | CPU | Memory | Procs | FSize | Expected Result |
|--------|-----|--------|-------|-------|-----------------|
| 1 | 5s | - | - | - | CPU limit hit |
| 2 | - | 256MB | - | - | Memory limit hit |
| 3 | - | - | 10 | - | Process limit hit |
| 4 | - | - | - | 100MB | File size limit hit |
| 5 | 5s | 256MB | - | - | CPU limit hit first |
| 6 | 30s | 100MB | - | - | Memory limit hit first |
| 7 | 5s | 256MB | 10 | 100MB | Multiple limits active |
| 8 | 0 | 0 | 0 | 0 | No limits (runs forever) |

---

## 🔍 What to Look For

### Success Criteria

#### CPU Limit Test:
✅ Process terminated by SIGXCPU  
✅ Execution time ≈ limit (±0.5s)  
✅ Output shows "CPU time limit exceeded"  
✅ Exit code indicates failure  

#### Memory Limit Test:
✅ malloc() fails OR process killed  
✅ Memory usage ≤ limit  
✅ System remains stable  
✅ No swap usage spike  

#### Process Limit Test:
✅ fork() fails with EAGAIN  
✅ Number of processes ≤ limit  
✅ System responsive  
✅ No zombie processes  

#### File Size Limit Test:
✅ Process terminated by SIGXFSZ  
✅ File size ≤ limit  
✅ Disk space not exhausted  
✅ Clean termination  

---

## 💬 Questions You'll Be Asked

### Q1: "How do you test that the sandbox actually works?"

**Answer**:
"We use **adversarial testing** - we write programs that intentionally try to violate limits:

1. **infinite_loop**: Tries to use unlimited CPU
2. **memory_hog**: Tries to allocate unlimited memory
3. **fork_bomb**: Tries to create unlimited processes
4. **file_size_test**: Tries to fill the disk

If the sandbox works, all these programs should **fail in specific ways**:
- CPU test → SIGXCPU after limit
- Memory test → malloc() fails or SIGKILL
- Fork test → fork() returns -1
- File test → SIGXFSZ after limit

We verify the sandbox **prevents** these attacks."

### Q2: "Why is memset() important in the memory test?"

**Answer**:
"Without memset(), the OS might not actually allocate memory:

```c
// Linux uses 'lazy allocation' / 'overcommit'
ptr = malloc(1 GB);  // OS says 'OK' but doesn't allocate RAM yet
                     // Just reserves virtual address space

// To force real allocation:
memset(ptr, 0, 1 GB);  // OS MUST allocate physical RAM now
                       // Page faults trigger actual allocation
```

Without memset(), our test would pass even if the limit wasn't working!"

### Q3: "What's the difference between a real fork bomb and your test?"

**Answer**:
"Safety!

**Real fork bomb**:
```c
while(1) fork();  // Each child ALSO forks
// Growth: 1→2→4→8→16→32→64→128→...
// Exponential! System crashes in seconds
```

**Our test**:
```c
while(1) {
    if (fork() == 0) {
        sleep(2);  // Child sleeps, doesn't fork
        exit(0);
    }
}
// Only parent forks → linear growth
// Safe with limits
```

Our test validates the defense without actually attacking the system."

### Q4: "How do you know the limits are enforced by the kernel, not just your program?"

**Answer**:
"We can verify kernel enforcement:

1. **Signals**: The kernel sends signals (SIGXCPU, SIGKILL, SIGXFSZ), not our program
2. **strace**: We can trace system calls:
```bash
strace ./sandbox --cpu=5 ./tests/infinite_loop
# Shows: setrlimit(RLIMIT_CPU, {rlim_cur=5, rlim_max=5})
```
3. **/proc**: Check process limits:
```bash
cat /proc/<pid>/limits
# Shows kernel-tracked limits
```

The kernel enforces limits **independently** of our program."

### Q5: "What happens if someone tries to bypass the limits?"

**Answer**:
"They **cannot** bypass kernel-level limits:

**Attempted bypasses**:
1. Call setrlimit() again → Can only LOWER limits, not raise
2. Fork new process → Inherits same limits
3. Exec new program → Limits persist across exec
4. Close file descriptors → Doesn't affect limits
5. Signal handlers → Can't prevent SIGXCPU/SIGKILL

The limits are in the **process control block (PCB)** in kernel memory. User-space programs cannot modify kernel memory."

### Q6: "How do you test that the GUI and sandbox work together?"

**Answer**:
"Integration testing workflow:

1. **Manual Testing**: Use GUI to run each test program
   - Set limits in GUI
   - Click Execute
   - Verify output matches expectations

2. **Automated Testing**: Script the test sequence
   - Build command arrays
   - Verify command construction
   - Check output parsing

3. **End-to-End**: Complete user workflow
   - User clicks quick command
   - Preset applied
   - Execution successful
   - Output displayed correctly

We test both **components separately** and **integrated together**."

---

## 🎯 Demo Script for Mentor

### 1. Explain Test Philosophy
"We use adversarial testing - programs that try to break the sandbox..."

### 2. Show Test Programs
```bash
# Open each test program
code tests/infinite_loop.c
code tests/memory_hog.c
code tests/fork_bomb.c
code tests/file_size_test.c

# Explain what each one does
```

### 3. Run Tests Live
```bash
# CPU test
echo "Testing CPU limit..."
./sandbox --cpu=5 ./tests/infinite_loop

# Memory test
echo "Testing memory limit..."
./sandbox --mem=256 ./tests/memory_hog

# Process test
echo "Testing process limit..."
./sandbox --procs=10 ./tests/fork_bomb

# File size test
echo "Testing file size limit..."
./sandbox --fsize=100 ./tests/file_size_test
```

### 4. Show Test Results
"Notice how each test fails in the expected way..."
- Point out SIGXCPU for CPU test
- Point out malloc() failure for memory test
- Point out fork() failure for process test
- Point out SIGXFSZ for file size test

### 5. Demonstrate GUI Testing
"Let me show the same tests through the GUI..."
- Open GUI
- Run CPU test through GUI
- Show real-time output
- Explain color-coded messages

### 6. Discuss Security
"These tests prove the sandbox is effective because..."
- Limits are kernel-enforced
- Attacks are prevented
- System remains stable

---

## ✅ Pre-Presentation Checklist

- [ ] Compile all test programs: `make -C tests`
- [ ] Run complete test suite: `./test_sandbox.sh`
- [ ] Verify all tests produce expected results
- [ ] Understand what each test program does
- [ ] Know expected output for each test
- [ ] Can explain signals (SIGXCPU, SIGKILL, SIGXFSZ)
- [ ] Can explain why memset() is needed
- [ ] Can explain fork bomb vs our safe test
- [ ] Know how to verify kernel enforcement
- [ ] Prepared to run live demos

---

**You ensure ZenCube works correctly and safely! Critical role!** 🛡️✅
