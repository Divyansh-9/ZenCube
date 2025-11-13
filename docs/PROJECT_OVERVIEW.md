# ZenCube Project - Complete Technical Overview

## 📋 Table of Contents
1. [Executive Summary](#executive-summary)
2. [Project Architecture](#project-architecture)
3. [Technical Components](#technical-components)
4. [System Flow](#system-flow)
5. [File Structure & Purpose](#file-structure--purpose)
6. [Technology Stack](#technology-stack)
7. [Security Model](#security-model)
8. [Performance Considerations](#performance-considerations)

---

## 🎯 Executive Summary

### What is ZenCube?
ZenCube is a **process sandboxing and resource limiting system** that allows safe execution of potentially dangerous or untrusted code. Think of it as a "safety container" for running programs with strict resource boundaries.

### The Problem It Solves
- **Security Risk**: Running untrusted code can compromise system security
- **Resource Exhaustion**: Malicious or buggy code can consume all CPU, memory, or disk space
- **Fork Bombs**: Programs that spawn infinite processes can crash the system
- **File System Abuse**: Programs can fill up disk space with large files

### Our Solution
A two-layer system:
1. **C-based Sandbox Core**: Low-level Linux system calls enforce hard resource limits
2. **Python GUI Frontend**: User-friendly interface for configuration and execution

### Real-World Applications
- 🎓 **Educational Platforms**: Safely run student code submissions (like LeetCode, HackerRank)
- 🔬 **CI/CD Pipelines**: Test untrusted code in isolated environments
- 🛡️ **Security Research**: Analyze malware behavior in controlled settings
- 🧪 **Software Testing**: Validate application behavior under resource constraints

---

## 🏗️ Project Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │         PySide6 Modern GUI (Python)                 │   │
│  │  • Resource limit configuration                     │   │
│  │  • Command input & quick commands                   │   │
│  │  • Real-time output display                         │   │
│  │  • Visual feedback & status                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 INTEGRATION & CONTROL LAYER                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │       Python Thread Manager & Executor              │   │
│  │  • Command building & validation                    │   │
│  │  • WSL/Native mode handling                         │   │
│  │  • Asynchronous execution (QThread)                 │   │
│  │  • Output streaming & parsing                       │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      SANDBOX CORE LAYER                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              C Binary (sandbox)                     │   │
│  │  • fork() - Process creation                        │   │
│  │  • setrlimit() - Resource enforcement               │   │
│  │  • execvp() - Command execution                     │   │
│  │  • waitpid() - Status monitoring                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                     LINUX KERNEL LAYER                       │
│  • Process isolation (separate PID)                         │
│  • Memory management (virtual address space)                │
│  • CPU scheduling (time slices)                             │
│  • Signal handling (SIGXCPU, SIGKILL, SIGXFSZ)             │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

```
User Action → GUI → Command Builder → Sandbox Binary → Kernel → Target Program
    ↑                                                                    ↓
    └──────────────────── Output Stream ←─────────────────────────────┘
```

---

## 🔧 Technical Components

### 1. Sandbox Core (sandbox.c)

**Technology**: C Programming Language  
**Size**: ~400 lines  
**Purpose**: Low-level process isolation and resource enforcement

#### Key System Calls:

**fork()** - Process Creation
```c
child_pid = fork();
// Creates exact copy of parent process
// Returns 0 in child, child's PID in parent
```
- Creates a new process (child) as a copy of the current process (parent)
- Child process has its own memory space and PID
- Allows parent to monitor child independently

**setrlimit()** - Resource Limiting
```c
struct rlimit rlim;
rlim.rlim_cur = cpu_seconds;    // Soft limit
rlim.rlim_max = cpu_seconds;    // Hard limit
setrlimit(RLIMIT_CPU, &rlim);
```
- Enforces hard limits at kernel level
- Four resource types supported:
  - `RLIMIT_CPU`: Maximum CPU time in seconds
  - `RLIMIT_AS`: Maximum address space (memory) in bytes
  - `RLIMIT_NPROC`: Maximum number of processes
  - `RLIMIT_FSIZE`: Maximum file size in bytes

**execvp()** - Program Execution
```c
execvp(argv[cmd_start_index], &argv[cmd_start_index]);
// Replaces current process image with new program
// Never returns if successful
```
- Replaces child process with target program
- Searches PATH for executable
- Preserves resource limits set by setrlimit()

**waitpid()** - Status Monitoring
```c
waitpid(child_pid, &status, 0);
// Waits for child process to finish
// Returns exit status in 'status' variable
```
- Parent waits for child to complete
- Captures exit code or termination signal
- Prevents zombie processes

#### Resource Limit Structure:
```c
typedef struct {
    int cpu_seconds;      // CPU time limit (0 = unlimited)
    long memory_mb;       // Memory in MB (0 = unlimited)
    int max_processes;    // Process count (0 = unlimited)
    long max_file_mb;     // File size in MB (0 = unlimited)
} ResourceLimits;
```

#### Signal Handling:
When limits are exceeded, Linux kernel sends signals:
- `SIGXCPU`: CPU time limit exceeded
- `SIGKILL`: Memory limit exceeded (kernel terminates)
- `SIGXFSZ`: File size limit exceeded

---

### 2. GUI Frontend (zencube_modern_gui.py)

**Technology**: PySide6 (Qt for Python)  
**Size**: ~1100 lines  
**Purpose**: User-friendly interface with modern design

#### Architecture Components:

**Custom Widgets** (Lines 36-285)
- `FlowLayout`: Responsive layout that wraps widgets
- `ModernButton`: Styled buttons with hover effects
- `ModernCard`: Card-based UI with shadows
- `ModernInput`: Styled text input fields
- `ModernCheckbox`: Custom checkboxes
- `ModernSpinBox`: Number input with validation

**Command Executor Thread** (Lines 287-344)
```python
class CommandExecutor(QThread):
    output_received = Signal(str)
    finished_signal = Signal(int)
    
    def run(self):
        self.process = subprocess.Popen(
            self.command_parts,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        # Stream output line by line
        for line in self.process.stdout:
            self.output_received.emit(line)
```
- Runs sandbox execution in separate thread
- Prevents GUI freezing during long operations
- Streams output in real-time
- Can be interrupted by user

**Main Window Class** (Lines 346-1100)
Key sections:
1. **Header**: Title, subtitle, settings button
2. **Command Section**: File browser, argument input, quick commands
3. **Limits Section**: Resource limit controls, presets
4. **Output Section**: Terminal-style output display
5. **Control Buttons**: Execute, stop, clear, toggle, help

#### GUI Features:

**Responsive Design**
- FlowLayout automatically wraps buttons on smaller screens
- Splitter allows resizing sections
- Minimum size constraints prevent UI breaking

**Visual Feedback**
- Color-coded output (green=success, red=error, yellow=warning)
- Loading animations during execution
- Shadow effects for depth perception
- Gradient backgrounds for modern look

**User Experience**
- Quick command presets for common tasks
- Preset configurations for different security levels
- Toggle terminal visibility to save space
- Keyboard shortcuts (Enter to execute)
- Status bar with system information

---

### 3. Integration Layer

**Command Building** (build_command method)
```python
def build_command(self):
    cmd_parts = []
    
    # Handle WSL/Native mode
    if self.use_wsl:
        cmd_parts = ["wsl", "./sandbox"]
    else:
        cmd_parts = ["./sandbox"]
    
    # Add resource limits
    if self.cpu_check.isChecked():
        cmd_parts.append(f"--cpu={self.cpu_spin.value()}")
    if self.mem_check.isChecked():
        cmd_parts.append(f"--mem={self.mem_spin.value()}")
    # ... more limits
    
    # Add target command
    cmd_parts.append(command)
    if args:
        cmd_parts.extend(args.split())
    
    return cmd_parts
```

**WSL Integration**
- Detects Windows platform automatically
- Converts Windows paths to WSL format
- Example: `C:\Users\...` → `/mnt/c/Users/...`
- Allows Windows users to run Linux sandbox

**Output Processing**
- Captures stdout and stderr in real-time
- Parses ANSI color codes
- Formats timestamps
- Detects error messages and highlights them

---

## 🔄 System Flow

### Complete Execution Flow

```
1. USER INPUT
   ↓
   User configures limits in GUI
   User selects command (browse or quick command)
   User clicks "Execute"

2. COMMAND BUILDING
   ↓
   Python validates input
   Builds command array: ["./sandbox", "--cpu=5", "--mem=256", "/bin/ls"]
   Handles WSL prefix if on Windows

3. THREAD CREATION
   ↓
   Creates CommandExecutor QThread
   Starts subprocess.Popen() with command
   GUI remains responsive

4. PROCESS FORKING
   ↓
   sandbox binary calls fork()
   Parent process: Waits for child
   Child process: Continues to next step

5. RESOURCE LIMITING
   ↓
   Child calls setrlimit() for each enabled limit
   Kernel enforces these limits immediately
   Limits are inherited by any child processes

6. PROGRAM EXECUTION
   ↓
   Child calls execvp() with target command
   Process image replaced with target program
   Program runs with enforced limits

7. MONITORING
   ↓
   Parent process waits with waitpid()
   Streams output to GUI in real-time
   Detects signals if limits exceeded

8. COMPLETION
   ↓
   Program exits or is killed by signal
   Parent captures exit status
   GUI displays results with color coding
   Thread signals completion

9. CLEANUP
   ↓
   Thread terminates
   File descriptors closed
   Memory freed
   GUI re-enables controls
```

### Example: Infinite Loop Test

```
User clicks "⏱️ CPU Test" button
  ↓
GUI sets: command="./tests/infinite_loop", cpu_limit=5
  ↓
Builds: ["./sandbox", "--cpu=5", "./tests/infinite_loop"]
  ↓
Sandbox creates child process
  ↓
Child sets RLIMIT_CPU = 5 seconds
  ↓
Child executes infinite_loop program
  ↓
infinite_loop runs: while(1) { counter++; }
  ↓
After ~5 seconds of CPU time:
  ↓
Kernel sends SIGXCPU to child
  ↓
Child process terminates
  ↓
Parent detects termination by signal
  ↓
Logs: "Process terminated by signal 24 (SIGXCPU)"
  ↓
GUI displays in RED: "⚠️ CPU time limit exceeded"
```

---

## 📁 File Structure & Purpose

### Core Files

```
ZenCube/
│
├── zencube/                          # Main project directory
│   │
│   ├── sandbox.c                     # ⭐ CORE: C sandbox implementation
│   │   • Purpose: Low-level process isolation
│   │   • Key Functions:
│   │       - main(): Entry point, orchestrates execution
│   │       - parse_arguments(): Parses command-line flags
│   │       - apply_resource_limits(): Calls setrlimit()
│   │       - log_message(): Timestamped logging
│   │   • Lines: 393
│   │   • Language: C
│   │
│   ├── sandbox                       # Compiled binary (executable)
│   │   • Generated by: make
│   │   • Size: ~20KB
│   │   • Platform: Linux ELF 64-bit
│   │
│   ├── Makefile                      # Build configuration
│   │   • Compiles sandbox.c → sandbox
│   │   • Flags: -Wall -Wextra -O2
│   │   • Targets: all, clean, test
│   │
│   ├── zencube_modern_gui.py        # ⭐ GUI: Modern PySide6 interface
│   │   • Purpose: User-friendly frontend
│   │   • Key Classes:
│   │       - ZenCubeModernGUI: Main window
│   │       - CommandExecutor: Async thread
│   │       - ModernButton/Card: Custom widgets
│   │   • Lines: ~1100
│   │   • Language: Python 3.x
│   │
│   ├── Zencube_gui.py               # Legacy GUI (older version)
│   │   • Purpose: Previous interface implementation
│   │   • Status: Kept for reference
│   │
│   ├── tests/                        # ⭐ TEST SUITE
│   │   │
│   │   ├── infinite_loop.c          # Test: CPU limit
│   │   │   • while(1) loop
│   │   │   • Expected: SIGXCPU after CPU limit
│   │   │
│   │   ├── infinite_loop            # Compiled test binary
│   │   │
│   │   ├── memory_hog.c             # Test: Memory limit
│   │   │   • Allocates memory in loop
│   │   │   • Expected: SIGKILL or allocation failure
│   │   │
│   │   ├── memory_hog               # Compiled test binary
│   │   │
│   │   ├── fork_bomb.c              # Test: Process limit
│   │   │   • while(1) fork()
│   │   │   • Expected: Fork fails, process limit enforced
│   │   │
│   │   ├── fork_bomb                # Compiled test binary
│   │   │
│   │   ├── file_size_test.c         # Test: File size limit
│   │   │   • Writes large data to file
│   │   │   • Expected: SIGXFSZ when limit exceeded
│   │   │
│   │   └── file_size_test           # Compiled test binary
│   │
│   ├── test_sandbox.sh              # Automated test script
│   │   • Runs all test programs
│   │   • Validates resource limits
│   │   • Checks exit codes
│   │
│   ├── test_phase2.sh               # Phase 2 specific tests
│   │   • Tests all resource limits
│   │   • Generates test report
│   │
│   ├── demo.sh                       # Quick demo script
│   │   • Shows sandbox capabilities
│   │   • User-friendly demonstrations
│   │
│   ├── README.md                     # Main documentation
│   │   • Usage instructions
│   │   • Feature list
│   │   • Examples
│   │
│   ├── QUICKSTART.md                # Getting started guide
│   ├── PHASE2_COMPLETE.md           # Phase 2 completion notes
│   ├── TEST_RESULTS.md              # Test execution results
│   ├── TESTING_CHECKLIST.md         # QA checklist
│   │
│   └── project_info.txt             # Project metadata
│
└── docs/                             # ⭐ NEW: Presentation documentation
    ├── PROJECT_OVERVIEW.md          # This file
    ├── ROLE_1_CORE_SANDBOX.md       # C developer role
    ├── ROLE_2_GUI_FRONTEND.md       # GUI developer role
    ├── ROLE_3_INTEGRATION.md        # Integration engineer role
    ├── ROLE_4_TESTING.md            # QA/Testing role
    └── QA_PREPARATION.md            # Mentor Q&A preparation
```

### File Categories

**Production Code**
- `sandbox.c`: Core functionality (YOU MUST UNDERSTAND THIS)
- `zencube_modern_gui.py`: User interface (YOU MUST UNDERSTAND THIS)

**Build System**
- `Makefile`: Compilation instructions
- `sandbox` (binary): Compiled executable

**Testing**
- `tests/*.c`: Test source code
- `tests/*` (no extension): Compiled test binaries
- `test_*.sh`: Automated test scripts

**Documentation**
- `README.md`: User documentation
- `docs/*.md`: Team presentation materials

---

## 💻 Technology Stack

### System Programming Layer
- **Language**: C (ANSI C99)
- **Standard Library**: POSIX.1-2001
- **System Calls**: Linux kernel API
- **Compiler**: GCC (GNU Compiler Collection)
- **Build System**: GNU Make

### GUI Layer
- **Language**: Python 3.8+
- **GUI Framework**: PySide6 (Qt 6.x)
- **Threading**: Qt QThread
- **Process Management**: subprocess module

### Platform Support
- **Primary**: Linux (Ubuntu, Debian, Fedora)
- **Windows**: Via WSL (Windows Subsystem for Linux)
- **macOS**: Limited support (Darwin kernel differences)

### Development Tools
- **Editor**: Any text editor / VS Code
- **Debugger**: GDB (GNU Debugger)
- **Version Control**: Git
- **Testing**: Bash scripts + custom test programs

---

## 🔒 Security Model

### Defense in Depth

**Layer 1: Input Validation**
- GUI validates user input before execution
- Checks for empty commands
- Validates numeric limits (positive integers)
- Prevents injection through argument parsing

**Layer 2: Process Isolation**
- `fork()` creates separate process with own PID
- Separate memory address space
- Cannot affect parent process
- Death of child doesn't crash parent

**Layer 3: Resource Enforcement**
- Kernel-level limits via `setrlimit()`
- Cannot be bypassed by user-space code
- Enforced before program execution
- Inherited by all child processes

**Layer 4: Privilege Separation**
- Sandbox runs with user's privileges (not root)
- Cannot escalate privileges
- Limited to user's file system access
- No network isolation (future enhancement)

### What ZenCube Protects Against

✅ **CPU Exhaustion**
- Infinite loops
- Computationally expensive algorithms
- Busy waiting

✅ **Memory Exhaustion**
- Memory leaks
- Excessive allocations
- Out-of-memory conditions

✅ **Fork Bombs**
- `while(1) fork()` attacks
- Process explosion
- System resource exhaustion

✅ **Disk Space Exhaustion**
- Large file creation
- Log flooding
- Uncontrolled file writes

### What ZenCube Does NOT Protect Against

❌ **Network Attacks**
- No network isolation
- Can still make network connections
- Can perform DDoS if network access available

❌ **File System Modification**
- Can still read/write files in user's directory
- No chroot or filesystem isolation
- Can potentially overwrite important files

❌ **Privilege Escalation**
- Relies on kernel security
- No additional MAC (Mandatory Access Control)
- Not a complete security solution

❌ **Side-Channel Attacks**
- Timing attacks
- Cache-based attacks
- Spectre/Meltdown-type vulnerabilities

### Security Best Practices

1. **Never run as root**: Always use unprivileged user account
2. **Set all limits**: Enable CPU, memory, process, and file limits
3. **Use strict preset**: For untrusted code, use the "Strict" preset
4. **Monitor output**: Check for suspicious behavior in logs
5. **Temporary directory**: Run sandboxed programs in isolated directories
6. **Regular updates**: Keep Linux kernel and system libraries updated

---

## ⚡ Performance Considerations

### Overhead Analysis

**Fork Overhead**
- Time: ~0.5-2ms on modern systems
- Memory: Copy-on-write (minimal initial overhead)
- Impact: Negligible for most use cases

**Exec Overhead**
- Time: ~1-5ms to load new program
- Memory: Replaces process image (no duplication)
- Impact: One-time cost at startup

**Resource Limit Overhead**
- Time: ~0.01ms per setrlimit() call
- Memory: None (kernel bookkeeping only)
- Impact: Virtually zero

**GUI Overhead**
- CPU: 1-2% during idle
- Memory: ~50-80MB for Qt framework
- Impact: Acceptable for desktop application

### Scalability

**Single Process Execution**
- Handles programs from microseconds to hours
- Memory scales with target program
- CPU overhead: <1%

**Concurrent Execution**
- GUI supports one execution at a time (by design)
- Could be extended for parallel execution
- Limited by available system resources

### Optimization Opportunities

1. **Binary Size**: Strip debug symbols (`strip sandbox`)
2. **Startup Time**: Preload GUI (keep resident in memory)
3. **Output Buffering**: Adjust buffer size for large outputs
4. **Thread Pool**: Reuse threads for multiple executions

---

## 📊 Metrics & Benchmarks

### Resource Usage (Sandbox Binary)
- **Binary Size**: ~20KB (stripped), ~60KB (with debug)
- **Memory Footprint**: ~2MB RSS (resident set size)
- **Startup Time**: ~2-5ms
- **Context Switch Time**: ~50-100 microseconds

### GUI Performance
- **Launch Time**: ~1-2 seconds (Qt initialization)
- **Memory Usage**: ~50-80MB
- **CPU Usage**: 1-2% idle, 5-10% during execution
- **Responsiveness**: 60 FPS UI updates

### Test Results
All tests passing ✅
- CPU Limit Test: SIGXCPU after 5.02 seconds
- Memory Limit Test: Process killed at 256MB
- Fork Bomb Test: Fork fails at 10 processes
- File Size Test: SIGXFSZ at 100MB

---

## 🎓 Learning Outcomes

By working on ZenCube, you learned:

### System Programming Concepts
- Process creation and management (`fork`, `exec`, `wait`)
- Resource limiting (`setrlimit`, `getrlimit`)
- Signal handling (SIGXCPU, SIGKILL, SIGXFSZ)
- Inter-process communication
- Memory management

### Software Engineering
- Modular design (separation of concerns)
- Error handling and logging
- User input validation
- Testing and quality assurance

### GUI Development
- Event-driven programming
- Asynchronous execution (threading)
- Responsive design
- User experience (UX) principles

### Security
- Sandboxing techniques
- Attack vectors (fork bombs, memory exhaustion)
- Defense in depth
- Privilege management

---

## 🚀 Future Enhancements

### Phase 3 (Potential)
- Filesystem isolation (chroot)
- Network namespace isolation
- Seccomp (system call filtering)
- Capability dropping

### Phase 4 (Advanced)
- Container-like isolation (cgroups)
- Multiple concurrent executions
- Execution history and statistics
- Custom limit profiles (save/load)

### GUI Improvements
- Syntax highlighting for commands
- Autocomplete for file paths
- Execution history browser
- Resource usage graphs (real-time)
- Dark mode theme

---

## 📞 Project Information

**Project Name**: ZenCube  
**Version**: 2.0 (Phase 2 Complete)  
**Team Size**: 4 developers  
**Development Time**: ~3 weeks  
**Lines of Code**: ~1500 (C + Python)  
**Test Coverage**: 4 test programs + 2 test scripts  

**Key Achievement**: Production-ready sandbox with modern GUI interface

---

## 🎯 Presentation Tips

### What to Emphasize
1. **Real-world applicability**: Like LeetCode/HackerRank
2. **Security importance**: Protecting against attacks
3. **Technical depth**: System calls and kernel interaction
4. **User experience**: Modern, intuitive GUI

### Demo Flow
1. Show GUI overview
2. Explain quick commands
3. Run CPU test (show SIGXCPU)
4. Run memory test (show memory limit)
5. Explain resource limits in detail
6. Show source code structure

### Common Questions (Be Prepared!)
- "How does fork() work?"
- "What happens when memory limit is exceeded?"
- "Can this be bypassed?"
- "What's the performance overhead?"
- "How is this different from Docker?"

See `QA_PREPARATION.md` for detailed Q&A preparation.

---

**END OF PROJECT OVERVIEW**
