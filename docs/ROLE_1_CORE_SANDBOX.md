# ROLE 1: Core Sandbox Developer (C Programming & System Calls)

## 👤 Your Role

You are responsible for the **low-level sandbox implementation** - the heart of ZenCube. Your expertise is in C programming, Linux system calls, and process management. You implemented the core security and resource limiting functionality.

---

## 📚 What You Need to Know Inside Out

### Your Primary File: `sandbox.c`

**Location**: `zencube/sandbox.c`  
**Size**: 393 lines  
**Language**: C (ANSI C99 with POSIX extensions)  
**Purpose**: Execute programs with enforced resource limits

---

## 🔍 Deep Dive: sandbox.c

### File Structure Overview

```c
Lines 1-15:    Header includes and defines
Lines 17-30:   Documentation and purpose
Lines 32-38:   ResourceLimits structure definition
Lines 40-45:   Function prototypes
Lines 47-73:   print_usage() - Help text
Lines 75-97:   log_message() - Logging utility
Lines 99-108:  log_command() - Command logging
Lines 110-113: timespec_diff() - Time calculation
Lines 115-166: parse_arguments() - Argument parsing
Lines 168-222: apply_resource_limits() - THE CORE FUNCTION
Lines 224-238: log_resource_limits() - Display limits
Lines 240-393: main() - Orchestration and execution
```

---

## 🧠 Critical Functions You Must Explain

### 1. main() Function - The Orchestrator

**Location**: Lines 246-393  
**Purpose**: Entry point that coordinates the entire sandboxing process

#### Step-by-Step Breakdown:

```c
int main(int argc, char *argv[]) {
    pid_t child_pid;
    int status;
    struct timespec start_time, end_time;
    ResourceLimits limits;
    int cmd_start_index;
```

**Variables Explained**:
- `child_pid`: Stores the process ID of the child process
- `status`: Holds exit status information from child
- `start_time/end_time`: For measuring execution time
- `limits`: Struct holding all resource limit values
- `cmd_start_index`: Index where actual command starts in argv[]

#### Phase 1: Parse Arguments (Lines 258-269)

```c
if (parse_arguments(argc, argv, &limits, &cmd_start_index) != 0) {
    fprintf(stderr, "\n");
    print_usage(argv[0]);
    return EXIT_FAILURE;
}

if (cmd_start_index >= argc) {
    fprintf(stderr, "Error: No command specified\n\n");
    print_usage(argv[0]);
    return EXIT_FAILURE;
}
```

**What happens**:
1. Calls `parse_arguments()` to extract limit values
2. Validates that a command was provided
3. Exits with error if validation fails

**Example command**: `./sandbox --cpu=5 --mem=256 /bin/ls -la`
- Parses: `--cpu=5` → limits.cpu_seconds = 5
- Parses: `--mem=256` → limits.memory_mb = 256
- Sets: `cmd_start_index = 3` (index of `/bin/ls`)

#### Phase 2: Fork Process (Lines 282-290)

```c
child_pid = fork();

if (child_pid == -1) {
    // Fork failed - critical error
    fprintf(stderr, "[Sandbox] Error: Failed to create child process: %s\n", 
            strerror(errno));
    return EXIT_FAILURE;
}
```

**The fork() System Call**:
- Creates an **exact copy** of the current process
- Returns **twice**:
  - Returns `0` in the child process
  - Returns child's PID in the parent process
  - Returns `-1` on failure

**Memory Layout After Fork**:
```
BEFORE fork():
┌─────────────────────┐
│   Parent Process    │
│   PID: 1234        │
│   Code + Data      │
└─────────────────────┘

AFTER fork():
┌─────────────────────┐        ┌─────────────────────┐
│   Parent Process    │        │   Child Process     │
│   PID: 1234        │        │   PID: 5678        │
│   fork() returns:   │        │   fork() returns:   │
│   5678             │        │   0                │
└─────────────────────┘        └─────────────────────┘
    (Waits for child)              (Executes command)
```

#### Phase 3: Child Process - Apply Limits (Lines 292-305)

```c
if (child_pid == 0) {
    /* This code ONLY runs in the child process */
    log_message("Child process created (PID: %d)", getpid());
    
    /* Apply resource limits */
    if (apply_resource_limits(&limits) != 0) {
        fprintf(stderr, "[Sandbox] Child Error: Failed to apply resource limits\n");
        exit(EXIT_FAILURE);
    }
```

**Key Point**: Resource limits are set BEFORE executing the target program. This ensures the target program cannot escape the limits.

#### Phase 4: Execute Target Program (Lines 307-318)

```c
    /* Replace process image with target command */
    if (execvp(argv[cmd_start_index], &argv[cmd_start_index]) == -1) {
        fprintf(stderr, "[Sandbox] Child Error: Failed to execute '%s': %s\n", 
                argv[cmd_start_index], strerror(errno));
        exit(EXIT_FAILURE);
    }
    
    /* This line should never be reached */
    exit(EXIT_FAILURE);
}
```

**The execvp() System Call**:
- **Replaces** the current process image with a new program
- **Never returns** if successful
- **Preserves**: PID, file descriptors, resource limits
- **Replaces**: Code, data, stack, heap

**Example**:
```c
// Before execvp(): Child is running sandbox code
execvp("/bin/ls", ["/bin/ls", "-la"]);
// After execvp(): Child is now running /bin/ls code
// The sandbox code is GONE - replaced entirely
```

#### Phase 5: Parent Process - Wait for Child (Lines 319-330)

```c
} else {
    /* This code ONLY runs in the parent process */
    log_message("Child PID: %d", child_pid);
    
    /* Wait for child process to complete */
    pid_t wait_result = waitpid(child_pid, &status, 0);
    
    /* Record end time */
    if (clock_gettime(CLOCK_MONOTONIC, &end_time) == -1) {
        log_message("Warning: Failed to get end time: %s", strerror(errno));
        execution_time = -1.0;
    } else {
        execution_time = timespec_diff(&start_time, &end_time);
    }
```

**The waitpid() System Call**:
- Parent **blocks** (waits) until child finishes
- Returns child's exit status in `status` parameter
- Prevents **zombie processes** (dead processes that haven't been reaped)

#### Phase 6: Analyze Exit Status (Lines 340-391)

```c
if (WIFEXITED(status)) {
    /* Child exited normally (called exit() or returned from main) */
    int exit_code = WEXITSTATUS(status);
    log_message("Process exited normally with status %d", exit_code);
    return exit_code;
    
} else if (WIFSIGNALED(status)) {
    /* Child was terminated by a signal */
    int signal_num = WTERMSIG(status);
    log_message("Process terminated by signal %d (%s)", 
               signal_num, strsignal(signal_num));
    
    /* Check for specific resource limit signals */
    if (signal_num == SIGXCPU) {
        log_message("⚠️  RESOURCE LIMIT VIOLATED: CPU time limit exceeded");
    } else if (signal_num == SIGKILL) {
        log_message("⚠️  Process was killed (possibly by memory limit)");
    } else if (signal_num == SIGXFSZ) {
        log_message("⚠️  RESOURCE LIMIT VIOLATED: File size limit exceeded");
    }
    
    return EXIT_FAILURE;
}
```

**Status Macros Explained**:
- `WIFEXITED(status)`: True if child exited normally
- `WEXITSTATUS(status)`: Extracts exit code (0-255)
- `WIFSIGNALED(status)`: True if child was killed by signal
- `WTERMSIG(status)`: Extracts signal number
- `WCOREDUMP(status)`: True if core dump was created

---

### 2. apply_resource_limits() - The Security Core

**Location**: Lines 168-222  
**Purpose**: Set kernel-level resource limits using setrlimit()

#### Complete Function Walkthrough:

```c
int apply_resource_limits(const ResourceLimits *limits) {
    struct rlimit rlim;
    
    /* Apply CPU time limit */
    if (limits->cpu_seconds > 0) {
        rlim.rlim_cur = limits->cpu_seconds;    // Soft limit
        rlim.rlim_max = limits->cpu_seconds;    // Hard limit
        
        if (setrlimit(RLIMIT_CPU, &rlim) != 0) {
            fprintf(stderr, "[Sandbox] Error: Failed to set CPU limit: %s\n", 
                    strerror(errno));
            return -1;
        }
        log_message("CPU limit set to %d seconds", limits->cpu_seconds);
    }
```

**The rlimit Structure**:
```c
struct rlimit {
    rlim_t rlim_cur;  // Soft limit (current limit)
    rlim_t rlim_max;  // Hard limit (ceiling for soft limit)
};
```

**Soft vs Hard Limits**:
- **Soft Limit**: The enforced limit. Process receives signal when exceeded.
- **Hard Limit**: Maximum value for soft limit. Only root can raise hard limit.
- In our case: **soft == hard** (strict enforcement)

#### CPU Limit (RLIMIT_CPU)

```c
if (limits->cpu_seconds > 0) {
    rlim.rlim_cur = limits->cpu_seconds;
    rlim.rlim_max = limits->cpu_seconds;
    setrlimit(RLIMIT_CPU, &rlim);
}
```

**What it does**:
- Limits **CPU time** (not wall-clock time)
- Measured in seconds
- When exceeded: Kernel sends `SIGXCPU` to process

**Example**:
- Limit: 5 seconds
- Program runs infinite loop: `while(1) {}`
- After 5 seconds of CPU time → SIGXCPU → Process terminates

**CPU Time vs Wall-Clock Time**:
```
Wall-clock time: Real-world time (includes sleep, I/O wait)
CPU time: Time actually spent executing on CPU

Example:
  sleep(10)  → Wall-clock: 10s, CPU time: ~0.001s
  while(1){} → Wall-clock: 5s, CPU time: 5s (100% CPU usage)
```

#### Memory Limit (RLIMIT_AS)

```c
if (limits->memory_mb > 0) {
    rlim.rlim_cur = (rlim_t)limits->memory_mb * 1024 * 1024;
    rlim.rlim_max = (rlim_t)limits->memory_mb * 1024 * 1024;
    setrlimit(RLIMIT_AS, &rlim);
}
```

**What it does**:
- Limits **virtual address space** (total memory)
- Includes: heap, stack, memory-mapped files, shared memory
- Measured in bytes (we convert MB to bytes)

**When exceeded**:
- `malloc()` returns `NULL`
- `mmap()` fails
- Stack overflow → `SIGSEGV`
- Kernel may send `SIGKILL`

**Example**:
```c
// Memory limit: 256 MB
char *big = malloc(300 * 1024 * 1024);  // Try to allocate 300 MB
if (big == NULL) {
    // malloc() failed - limit exceeded
    printf("Out of memory!\n");
}
```

#### Process Limit (RLIMIT_NPROC)

```c
if (limits->max_processes > 0) {
    rlim.rlim_cur = limits->max_processes;
    rlim.rlim_max = limits->max_processes;
    setrlimit(RLIMIT_NPROC, &rlim);
}
```

**What it does**:
- Limits total number of processes user can create
- Counts **all processes** owned by the user's UID
- Prevents fork bombs

**Fork Bomb Example**:
```c
// Without limit: Creates infinite processes, crashes system
while (1) {
    fork();  // Each child also forks → exponential growth
}

// With limit (e.g., 10 processes):
// After 10 processes created, fork() returns -1 (EAGAIN)
// System remains stable
```

**Why this is critical**:
```
Time    Processes Created    Total Processes
0s      1 (initial)          1
1s      1 fork → 2           2
2s      2 fork → 4           4
3s      4 fork → 8           8
4s      8 fork → 16          16
5s      16 fork → 32         32
...
10s     ~1024 processes      1024 (system unusable!)

With limit of 10: Stops at 10, system safe
```

#### File Size Limit (RLIMIT_FSIZE)

```c
if (limits->max_file_mb > 0) {
    rlim.rlim_cur = (rlim_t)limits->max_file_mb * 1024 * 1024;
    rlim.rlim_max = (rlim_t)limits->max_file_mb * 1024 * 1024;
    setrlimit(RLIMIT_FSIZE, &rlim);
}
```

**What it does**:
- Limits maximum size of files created by process
- Measured in bytes
- When exceeded: Kernel sends `SIGXFSZ`

**Example**:
```c
// Limit: 100 MB
FILE *f = fopen("output.dat", "w");
for (int i = 0; i < 200; i++) {
    // Try to write 200 MB (1 MB per iteration)
    fwrite(buffer, 1, 1024*1024, f);  
}
// After writing 100 MB → SIGXFSZ → Process terminates
```

---

### 3. parse_arguments() - Input Validation

**Location**: Lines 117-166  
**Purpose**: Parse command-line arguments and extract resource limits

#### Function Logic:

```c
int parse_arguments(int argc, char *argv[], 
                   ResourceLimits *limits, int *cmd_start_index) {
    int i = 1;
    
    /* Initialize all limits to 0 (unlimited) */
    limits->cpu_seconds = 0;
    limits->memory_mb = 0;
    limits->max_processes = 0;
    limits->max_file_mb = 0;
```

**Why initialize to 0?**
- 0 means "unlimited" in setrlimit()
- User can choose which limits to enable
- Default: no restrictions

#### Parsing Loop:

```c
while (i < argc && argv[i][0] == '-') {
    if (strcmp(argv[i], "--help") == 0) {
        print_usage(argv[0]);
        exit(EXIT_SUCCESS);
        
    } else if (strncmp(argv[i], "--cpu=", 6) == 0) {
        // Extract number after "=" character
        limits->cpu_seconds = atoi(argv[i] + 6);
        
        if (limits->cpu_seconds < 0) {
            fprintf(stderr, "Error: Invalid CPU limit: %s\n", argv[i] + 6);
            return -1;
        }
```

**Parsing Technique**:
- `strncmp(argv[i], "--cpu=", 6)`: Check if argument starts with "--cpu="
- `argv[i] + 6`: Skip past "--cpu=" to get the number
- `atoi()`: Convert string to integer

**Example**:
```
Input: "--cpu=5"
       argv[i] = "--cpu=5"
       argv[i] + 6 = "5"
       atoi("5") = 5
       limits->cpu_seconds = 5
```

---

## 🎓 Key Concepts You Must Explain

### Process States

```
┌─────────────────────────────────────────────────────────┐
│                    Process Lifecycle                     │
└─────────────────────────────────────────────────────────┘

1. CREATED (fork)
   │
   ├─► Parent Process (original)
   │   └─► Calls waitpid() → WAITING state
   │
   └─► Child Process (new copy)
       ├─► Applies resource limits
       ├─► Calls execvp() → RUNNING state
       └─► Executes target program
           │
           ├─► Exits normally → ZOMBIE → Reaped by parent
           └─► Killed by signal → ZOMBIE → Reaped by parent
```

### Signal Handling

**Signals Explained**:
Signals are asynchronous notifications sent by the kernel to a process.

**Resource Limit Signals**:
- `SIGXCPU` (24): CPU time limit exceeded
- `SIGKILL` (9): Forceful termination (cannot be caught)
- `SIGXFSZ` (25): File size limit exceeded
- `SIGSEGV` (11): Segmentation fault (often from memory limit)

**Signal Flow**:
```
1. Process exceeds resource limit
   ↓
2. Kernel detects violation
   ↓
3. Kernel sends signal to process
   ↓
4. Process has no signal handler → Default action
   ↓
5. Default action: Terminate process
   ↓
6. Parent's waitpid() returns
   ↓
7. Parent checks WIFSIGNALED(status)
   ↓
8. Parent extracts signal number with WTERMSIG(status)
```

### Virtual Memory

**Why RLIMIT_AS (Address Space)?**
- Virtual memory includes ALL memory used by process
- Physical memory (RAM) + Swap space
- Includes: code, data, heap, stack, shared libraries

**Memory Breakdown**:
```
Virtual Address Space (RLIMIT_AS):
┌─────────────────────────────────┐
│  Kernel Space (not counted)     │
├─────────────────────────────────┤ ← High addresses
│  Stack (local variables)        │
│         ↓ grows down            │
│                                 │
│  Memory-mapped files            │
│                                 │
│         ↑ grows up              │
│  Heap (malloc allocations)      │
├─────────────────────────────────┤
│  BSS (uninitialized data)       │
│  Data (initialized data)        │
│  Text (program code)            │
└─────────────────────────────────┘ ← Low addresses (0x00000000)
```

---

## 🧪 Testing Your Code

### Test Cases You Should Run:

#### 1. CPU Limit Test
```bash
./sandbox --cpu=5 ./tests/infinite_loop
```
**Expected**:
- Process runs for ~5 seconds
- Output: "Process terminated by signal 24 (SIGXCPU)"
- Exit code: Non-zero (failure)

#### 2. Memory Limit Test
```bash
./sandbox --mem=256 ./tests/memory_hog
```
**Expected**:
- Process allocates memory until 256MB limit
- Either: malloc() fails gracefully, or SIGKILL
- Exit code: Non-zero

#### 3. Process Limit Test
```bash
./sandbox --procs=10 ./tests/fork_bomb
```
**Expected**:
- Process creates ~10 processes
- fork() starts returning -1
- System remains stable
- Exit code: Depends on test program

#### 4. File Size Limit Test
```bash
./sandbox --fsize=100 ./tests/file_size_test
```
**Expected**:
- Creates file up to 100MB
- Output: "Process terminated by signal 25 (SIGXFSZ)"
- File size: ≤ 100MB

---

## 💬 Questions You'll Be Asked

### Q1: "How does fork() work internally?"

**Answer**:
"fork() is a system call that creates a child process by **copying** the parent's process control block (PCB) and memory. However, it uses **copy-on-write** optimization:

1. **Virtual memory**: Child gets same page table entries as parent
2. **No copying yet**: Both processes share physical memory pages (read-only)
3. **On write**: When either process modifies memory, kernel copies that page
4. **Return value**: fork() returns twice - 0 in child, child's PID in parent

This makes fork() very fast despite creating a full process copy."

**Code Example**:
```c
pid_t pid = fork();
if (pid == 0) {
    printf("I'm the child, PID: %d\n", getpid());
} else {
    printf("I'm the parent, child PID: %d\n", pid);
}
```

### Q2: "Why use execvp() instead of exec()?"

**Answer**:
"execvp() has two advantages over basic exec():

1. **'v' suffix**: Takes argv as an array (vector), easier to use
2. **'p' suffix**: Searches PATH environment variable automatically

So we can write:
```c
execvp(\"ls\", [\"ls\", \"-l\"]);  // Finds /bin/ls automatically
```

Instead of:
```c
execl(\"/bin/ls\", \"ls\", \"-l\", NULL);  // Must know full path
```

This makes our sandbox more user-friendly."

### Q3: "What happens if the target program tries to bypass the limits?"

**Answer**:
"It **cannot bypass** the limits because setrlimit() enforces limits at the **kernel level**:

1. **Kernel enforcement**: Limits are stored in process control block (PCB)
2. **No escape**: User-space programs cannot modify PCB
3. **Inherited**: Child processes inherit limits (can only make stricter)
4. **Hardware-backed**: CPU time tracked by hardware timer interrupts

Even if a malicious program tried to call setrlimit() itself, it can only **lower** limits, never raise them above the hard limit."

### Q4: "What's the difference between CPU time and wall-clock time?"

**Answer**:
"CPU time is the actual time spent executing on the CPU core. Wall-clock time is real-world elapsed time.

**Example**:
```c
sleep(10);  // Wall-clock: 10 seconds, CPU time: ~0 seconds
            // (Process is sleeping, not using CPU)

while(1);   // Wall-clock: 5s, CPU time: 5s
            // (Process constantly using 100% of one CPU core)
```

Our sandbox limits **CPU time** because that's what we want to restrict - actual computation. Otherwise, a malicious program could just call sleep() to avoid termination!"

### Q5: "Why do we fork() before applying limits?"

**Answer**:
"We fork() first for two reasons:

1. **Isolation**: If we applied limits in the parent, they would affect the sandbox itself
2. **Safety**: Parent needs unlimited resources to monitor and log the child's behavior

The child inherits a **clean slate**, applies limits, then executes the target program. The parent remains unrestricted and can always clean up after the child."

### Q6: "Can this sandbox be used in production?"

**Answer**:
"For **basic resource limiting**, yes. But production systems need additional security:

**What we have** ✅:
- CPU, memory, process, file size limits
- Process isolation (separate PID)
- No root privileges required

**What we're missing** ❌:
- Network isolation (can still make connections)
- Filesystem isolation (can read/write user's files)
- System call filtering (seccomp)
- Capability dropping

For production, we'd add **containers** (like Docker) or **seccomp-bpf** for syscall filtering."

---

## 🎯 Demo Script for Mentor

### 1. Show the Code Structure
```bash
# Open sandbox.c
code zencube/sandbox.c

# Explain structure:
# - Lines 1-45: Setup and prototypes
# - Lines 168-222: apply_resource_limits() - THE CORE
# - Lines 246-393: main() - Orchestration
```

### 2. Walk Through main() Function
"Let me explain the execution flow..."
- Point to fork() at line 282
- Explain child/parent split
- Show apply_resource_limits() call
- Show execvp() call
- Show waitpid() in parent

### 3. Deep Dive into apply_resource_limits()
"This is where the magic happens..."
- Show setrlimit() calls
- Explain each limit type
- Discuss kernel enforcement

### 4. Run Live Demo
```bash
# Compile
cd zencube
make clean
make

# Test CPU limit
./sandbox --cpu=5 ./tests/infinite_loop
# Watch it terminate after 5 seconds with SIGXCPU

# Test memory limit  
./sandbox --mem=256 ./tests/memory_hog
# Watch it fail to allocate more than 256MB

# Explain output as it runs
```

### 5. Answer Questions
"The key insight is that **kernel enforcement** makes this secure..."

---

## 📝 Cheat Sheet for Presentation

### System Calls Quick Reference

| System Call | Purpose | Returns |
|------------|---------|---------|
| `fork()` | Create child process | 0 in child, PID in parent, -1 on error |
| `execvp(cmd, args)` | Replace process with new program | Never returns on success, -1 on error |
| `waitpid(pid, &status, 0)` | Wait for child to finish | Child's PID, -1 on error |
| `setrlimit(res, &rlim)` | Set resource limit | 0 on success, -1 on error |

### Resource Limits Quick Reference

| Limit | Constant | Effect When Exceeded |
|-------|----------|---------------------|
| CPU time | `RLIMIT_CPU` | SIGXCPU sent |
| Memory | `RLIMIT_AS` | malloc() fails, SIGKILL |
| Processes | `RLIMIT_NPROC` | fork() fails |
| File size | `RLIMIT_FSIZE` | SIGXFSZ sent |

### Important Macros

| Macro | Purpose |
|-------|---------|
| `WIFEXITED(status)` | True if exited normally |
| `WEXITSTATUS(status)` | Get exit code |
| `WIFSIGNALED(status)` | True if killed by signal |
| `WTERMSIG(status)` | Get signal number |

---

## ✅ Pre-Presentation Checklist

- [ ] Compile sandbox successfully: `make clean && make`
- [ ] Run all test programs once
- [ ] Read through sandbox.c completely
- [ ] Understand every system call used
- [ ] Practice explaining fork/exec/wait flow
- [ ] Prepare to draw process diagrams on board
- [ ] Have GDB ready for debugging demo (optional)
- [ ] Know the line numbers of key functions

---

**You've got this! You understand the core of ZenCube. Own it!** 🚀
