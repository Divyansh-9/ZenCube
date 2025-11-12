# ROLE 3: Integration Engineer (Python-C Bridge & Process Management)

## 👤 Your Role

You are the **bridge between the GUI and the C sandbox** - the integration layer. Your expertise is in Python subprocess management, cross-platform compatibility (WSL), command building, process control, and output handling.

---

## 📚 What You Need to Know Inside Out

### Your Primary Responsibilities

1. **Command Building**: Convert GUI state → executable command
2. **Process Management**: Execute sandbox with subprocess
3. **WSL Integration**: Handle Windows Subsystem for Linux
4. **Output Streaming**: Capture and forward stdout/stderr
5. **Error Handling**: Graceful failure recovery
6. **State Management**: Track execution status

---

## 🔗 The Integration Layer

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    GUI Layer (PySide6)                    │
│  User clicks Execute → Triggers execute_command()         │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│              YOUR LAYER: Integration                      │
│                                                           │
│  1. build_command() → Construct command array            │
│  2. CommandExecutor → Spawn subprocess                    │
│  3. Stream output → Send to GUI via signals              │
│  4. Monitor status → Handle completion/errors            │
└──────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────┐
│               C Sandbox (sandbox binary)                  │
│  Receives: ["./sandbox", "--cpu=5", "/bin/ls"]          │
│  Executes: fork() → setrlimit() → execvp()              │
└──────────────────────────────────────────────────────────┘
```

---

## 🛠️ Deep Dive: Command Building

### build_command() Method (Lines 893-930)

**Purpose**: Transform GUI settings into executable command array

#### Input Sources:

```python
# From GUI widgets:
command = self.command_input.text()          # "/bin/ls"
args = self.args_input.text()                # "-la"
cpu_enabled = self.cpu_check.isChecked()     # True
cpu_value = self.cpu_spin.value()            # 5
mem_enabled = self.mem_check.isChecked()     # True
mem_value = self.mem_spin.value()            # 256
use_wsl = self.use_wsl                       # True/False
```

#### Step-by-Step Construction:

```python
def build_command(self):
    """Build command array from GUI state"""
    
    # Step 1: Get and validate user input
    command = self.command_input.text().strip()
    args = self.args_input.text().strip()
    
    if not command:
        self.log_output("❌ Error: No command specified\n", "error")
        return None  # Early return on validation failure
```

**Why strip()?**
- Removes leading/trailing whitespace
- Prevents errors from accidental spaces
- Example: `" /bin/ls "` → `"/bin/ls"`

#### Step 2: Handle WSL Path Conversion

```python
    # Step 2: Convert Windows paths to WSL if needed
    if self.use_wsl and ':' in command:
        # Windows path detected: C:\path\to\file
        drive = command[0].lower()              # 'c'
        path = command[2:].replace('\\', '/')   # '\path\to\file' → '/path/to/file'
        command = f"/mnt/{drive}{path}"         # '/mnt/c/path/to/file'
        
        self.log_output(f"🔄 Converted to WSL path: {command}\n", "info")
```

**Path Conversion Examples**:
```python
# Windows → WSL
"C:\\Users\\User\\test.exe"  →  "/mnt/c/Users/User/test.exe"
"D:\\Projects\\app"          →  "/mnt/d/Projects/app"

# Linux/WSL paths (no conversion)
"/bin/ls"                    →  "/bin/ls" (unchanged)
"./sandbox"                  →  "./sandbox" (unchanged)
```

#### Step 3: Initialize Command Array

```python
    # Step 3: Start building command array
    if self.use_wsl:
        # WSL: Need to prefix with 'wsl' command
        cmd_parts = ["wsl", "./sandbox"]
    else:
        # Native Linux: Direct execution
        cmd_parts = ["./sandbox"]
```

**WSL Mode**:
```python
cmd_parts = ["wsl", "./sandbox", ...]
# Windows → WSL → sandbox → target program
```

**Native Mode**:
```python
cmd_parts = ["./sandbox", ...]
# sandbox → target program
```

#### Step 4: Add Resource Limit Flags

```python
    # Step 4: Add resource limits based on checkboxes
    if self.cpu_check.isChecked():
        cmd_parts.append(f"--cpu={self.cpu_spin.value()}")
    
    if self.mem_check.isChecked():
        cmd_parts.append(f"--mem={self.mem_spin.value()}")
    
    if self.procs_check.isChecked():
        cmd_parts.append(f"--procs={self.procs_spin.value()}")
    
    if self.fsize_check.isChecked():
        cmd_parts.append(f"--fsize={self.fsize_spin.value()}")
```

**Important**: Order matters!
```python
# Correct:
["./sandbox", "--cpu=5", "--mem=256", "/bin/ls", "-la"]
#  ↑ program  ↑ options          ↑ command ↑ command args

# Wrong:
["./sandbox", "/bin/ls", "--cpu=5"]  # Options after command won't work!
```

#### Step 5: Append Command and Arguments

```python
    # Step 5: Add the target command
    cmd_parts.append(command)
    
    # Step 6: Split and add arguments
    if args:
        # Split by whitespace: "-l -a" → ["-l", "-a"]
        cmd_parts.extend(args.split())
    
    return cmd_parts
```

**Argument Splitting**:
```python
args = "-l -a --color"
args.split() → ["-l", "-a", "--color"]

cmd_parts.extend(["-l", "-a", "--color"])
# Result: ["./sandbox", "--cpu=5", "/bin/ls", "-l", "-a", "--color"]
```

#### Complete Example:

```python
# GUI State:
# - Command: "./tests/infinite_loop"
# - CPU: Enabled, 5 seconds
# - Memory: Enabled, 256 MB
# - Processes: Disabled
# - File Size: Disabled
# - Arguments: (empty)
# - WSL: Disabled

# Result:
[
    "./sandbox",
    "--cpu=5",
    "--mem=256",
    "./tests/infinite_loop"
]
```

```python
# GUI State (Windows):
# - Command: "C:\Users\test.exe"
# - CPU: Enabled, 10 seconds
# - WSL: Enabled

# Result:
[
    "wsl",
    "./sandbox",
    "--cpu=10",
    "/mnt/c/Users/test.exe"
]
```

---

## 🧵 Process Management: CommandExecutor

### CommandExecutor Thread (Lines 303-342)

**Purpose**: Execute command asynchronously without blocking GUI

#### Class Definition:

```python
class CommandExecutor(QThread):
    """Thread for executing commands asynchronously"""
    
    # Signals for communication with main thread
    output_received = Signal(str)    # Emitted for each output line
    finished_signal = Signal(int)    # Emitted when process exits
    
    def __init__(self, command_parts):
        super().__init__()
        self.command_parts = command_parts  # Command array
        self.process = None                 # subprocess.Popen object
```

#### The run() Method - Core Execution Logic:

```python
    def run(self):
        """Executed in separate thread when start() is called"""
        try:
            # Create subprocess
            self.process = subprocess.Popen(
                self.command_parts,          # Command to execute
                stdout=subprocess.PIPE,      # Capture stdout
                stderr=subprocess.STDOUT,    # Merge stderr into stdout
                text=True,                   # Decode bytes → str
                bufsize=1                    # Line-buffered
            )
```

**subprocess.Popen Arguments Explained**:

| Argument | Value | Purpose |
|----------|-------|---------|
| `args` | `command_parts` | Command and arguments as list |
| `stdout` | `subprocess.PIPE` | Capture output (don't print to console) |
| `stderr` | `subprocess.STDOUT` | Merge error messages into stdout |
| `text` | `True` | Return strings (not bytes) |
| `bufsize` | `1` | Line-buffered (flush after each line) |

**Why merge stderr into stdout?**
```python
# Without merge:
# stdout: "Starting program..."
# stderr: "Warning: something"
# stdout: "Done"
# → Output interleaved incorrectly in GUI

# With merge (stderr=STDOUT):
# stdout: "Starting program..."
# stdout: "Warning: something"
# stdout: "Done"
# → Correct chronological order
```

#### Output Streaming:

```python
            # Stream output line by line
            for line in self.process.stdout:
                # Send each line to GUI via signal
                self.output_received.emit(line)
```

**Why line-by-line streaming?**
1. **Real-time feedback**: User sees output as it happens
2. **Memory efficient**: Don't accumulate all output in memory
3. **Responsive**: GUI updates smoothly

**Example**:
```python
# Program output:
# Line 1: "Starting..."
# Line 2: "Processing..."
# Line 3: "Done!"

# GUI receives:
output_received.emit("Starting...\n")    → Updates GUI immediately
output_received.emit("Processing...\n")  → Updates GUI immediately
output_received.emit("Done!\n")          → Updates GUI immediately
```

#### Process Completion:

```python
            # Wait for process to finish
            exit_code = self.process.wait()
            
            # Notify GUI that execution finished
            self.finished_signal.emit(exit_code)
```

**Exit Codes**:
- `0`: Success
- `1-255`: Error (program-specific)
- Negative: Terminated by signal (e.g., -9 for SIGKILL)

#### Error Handling:

```python
        except Exception as e:
            # Handle any errors (file not found, permission denied, etc.)
            error_msg = f"❌ Execution Error: {str(e)}\n"
            self.output_received.emit(error_msg)
            self.finished_signal.emit(-1)  # -1 indicates failure
```

**Common Errors**:
- `FileNotFoundError`: Sandbox binary not found
- `PermissionError`: Sandbox not executable
- `OSError`: System-level error

#### Stop Method:

```python
    def stop(self):
        """Terminate the running process"""
        if self.process:
            self.process.terminate()  # Send SIGTERM
            try:
                self.process.wait(timeout=5)  # Wait up to 5 seconds
            except subprocess.TimeoutExpired:
                self.process.kill()  # Force kill with SIGKILL
```

**Graceful Shutdown**:
1. Try `terminate()` (SIGTERM - allows cleanup)
2. Wait 5 seconds
3. If still running: `kill()` (SIGKILL - force terminate)

---

## 🎛️ Execution Flow

### Complete Execution Sequence:

```
1. USER CLICKS EXECUTE BUTTON
   ↓
2. execute_command() CALLED
   ↓
3. build_command() CONSTRUCTS ARRAY
   ["./sandbox", "--cpu=5", "/bin/ls"]
   ↓
4. CREATE CommandExecutor THREAD
   executor = CommandExecutor(cmd_parts)
   ↓
5. CONNECT SIGNALS
   output_received → log_output()
   finished_signal → on_command_finished()
   ↓
6. START THREAD
   executor.start() → Calls run() in new thread
   ↓
   ┌─────────────────────────────────────────────┐
   │         THREAD EXECUTION (Parallel)         │
   │                                             │
   │  7. subprocess.Popen() CREATES PROCESS     │
   │     ↓                                       │
   │  8. SANDBOX BINARY EXECUTES                │
   │     ↓                                       │
   │  9. OUTPUT STREAMS LINE BY LINE            │
   │     for line in stdout:                    │
   │         output_received.emit(line) ────┐   │
   │     ↓                                  │   │
   │  10. PROCESS FINISHES                  │   │
   │      finished_signal.emit(exit_code) ──┼─┐ │
   └────────────────────────────────────────┼─┼─┘
                                            ↓ ↓
   ┌────────────────────────────────────────┐ │
   │        MAIN THREAD (GUI)               │ │
   │                                        │ │
   │  11. log_output(line) ←────────────────┘ │
   │      Updates QTextEdit                   │
   │      ↓                                   │
   │  12. on_command_finished(code) ←─────────┘
   │      Re-enables buttons                  │
   │      Shows completion message            │
   └──────────────────────────────────────────┘
```

---

## 🖥️ WSL Integration

### Why WSL Support?

**Problem**: Windows doesn't support Linux system calls (fork, setrlimit, etc.)

**Solution**: Use WSL (Windows Subsystem for Linux)
- WSL runs a real Linux kernel on Windows
- Can execute Linux binaries
- Shares file system with Windows

### WSL Detection:

```python
# In __init__():
self.use_wsl = platform.system() == "Windows"
```

**platform.system() returns**:
- `"Windows"` → Use WSL
- `"Linux"` → Native execution
- `"Darwin"` → macOS (limited support)

### Path Conversion:

**Windows File System**:
```
C:\Users\Kamal\Documents\sandbox
D:\Projects\test.exe
```

**WSL File System**:
```
/mnt/c/Users/Kamal/Documents/sandbox
/mnt/d/Projects/test.exe
```

**Conversion Logic**:
```python
def convert_to_wsl_path(windows_path):
    """Convert Windows path to WSL format"""
    
    # Check if it's a Windows path (has drive letter)
    if ':' not in windows_path:
        return windows_path  # Already Linux-style path
    
    # Extract drive letter
    drive = windows_path[0].lower()  # 'C' → 'c'
    
    # Get path after "C:\"
    path = windows_path[2:]  # "C:\Users\..." → "\Users\..."
    
    # Replace backslashes with forward slashes
    path = path.replace('\\', '/')  # "\Users\..." → "/Users/..."
    
    # Construct WSL path
    wsl_path = f"/mnt/{drive}{path}"  # "/mnt/c/Users/..."
    
    return wsl_path
```

**Examples**:
```python
convert_to_wsl_path("C:\\Windows\\System32\\cmd.exe")
# Returns: "/mnt/c/Windows/System32/cmd.exe"

convert_to_wsl_path("D:\\Projects\\test")
# Returns: "/mnt/d/Projects/test"

convert_to_wsl_path("/bin/ls")
# Returns: "/bin/ls" (no conversion needed)
```

### WSL Command Execution:

```python
# Windows (WSL Mode):
cmd = ["wsl", "./sandbox", "--cpu=5", "/bin/ls"]
#      ↑ WSL wrapper

# Linux (Native Mode):
cmd = ["./sandbox", "--cpu=5", "/bin/ls"]
#      ↑ Direct execution
```

**What happens in WSL mode**:
1. Windows starts `wsl.exe`
2. WSL starts Linux environment
3. Linux executes `./sandbox`
4. Sandbox executes `/bin/ls`
5. Output flows back through WSL to Windows

---

## 📊 Output Handling

### log_output() Method (Lines 1014-1034)

**Purpose**: Display output in terminal with color coding

```python
def log_output(self, message, msg_type=None):
    """Add formatted message to output display"""
    
    # Get cursor at end of text
    cursor = self.output_text.textCursor()
    cursor.movePosition(QTextCursor.End)
    
    # Apply color based on message type
    if msg_type == "error":
        # Red for errors
        cursor.insertHtml(f'<span style="color: #ff6b6b;">{message}</span>')
    
    elif msg_type == "success":
        # Green for success
        cursor.insertHtml(f'<span style="color: #51cf66;">{message}</span>')
    
    elif msg_type == "warning":
        # Yellow for warnings
        cursor.insertHtml(f'<span style="color: #ffd93d;">{message}</span>')
    
    elif msg_type == "info":
        # Blue for info
        cursor.insertHtml(f'<span style="color: #74c0fc;">{message}</span>')
    
    else:
        # Default (white/green terminal color)
        cursor.insertText(message)
    
    # Update cursor position
    self.output_text.setTextCursor(cursor)
    
    # Auto-scroll to bottom
    self.output_text.ensureCursorVisible()
```

### Message Types:

| Type | Color | Use Case | Example |
|------|-------|----------|---------|
| `error` | Red | Errors, failures | "❌ Command failed" |
| `success` | Green | Successful operations | "✅ Execution complete" |
| `warning` | Yellow | Warnings | "⚠️ CPU limit exceeded" |
| `info` | Blue | Informational | "🔄 Starting command..." |
| `None` | Default | Normal output | Program stdout |

### Output Examples:

```python
# Error message
self.log_output("❌ Error: Sandbox not found\n", "error")
# → Red text in terminal

# Success message
self.log_output("✅ Process completed successfully\n", "success")
# → Green text in terminal

# Process output (no type)
self.log_output("Hello, World!\n")
# → Normal terminal color (green on dark background)
```

---

## 🎮 State Management

### Execution State Tracking:

```python
# Before execution:
self.executor = None
self.execute_btn.setEnabled(True)
self.stop_btn.setEnabled(False)

# During execution:
self.executor = CommandExecutor(cmd)
self.execute_btn.setEnabled(False)  # Prevent double-execution
self.stop_btn.setEnabled(True)      # Allow stopping

# After execution:
self.executor = None
self.execute_btn.setEnabled(True)   # Allow new execution
self.stop_btn.setEnabled(False)     # Disable stop button
```

### on_command_finished() Handler:

```python
def on_command_finished(self, exit_code):
    """Called when command execution completes"""
    
    self.log_output("\n" + "=" * 80 + "\n", "info")
    
    if exit_code == 0:
        # Success
        self.log_output("✅ Execution completed successfully\n", "success")
    else:
        # Failure
        self.log_output(f"❌ Execution failed with exit code: {exit_code}\n", "error")
    
    self.log_output("=" * 80 + "\n", "info")
    
    # Reset button states
    self.execute_btn.setEnabled(True)
    self.stop_btn.setEnabled(False)
    
    # Clean up executor
    self.executor = None
```

---

## 🐛 Error Handling

### Common Errors and Solutions:

#### 1. Sandbox Not Found

```python
# Error:
FileNotFoundError: [Errno 2] No such file or directory: './sandbox'

# Solution in detect_sandbox_path():
def detect_sandbox_path(self):
    """Try multiple locations for sandbox binary"""
    possible_paths = [
        "./sandbox",
        os.path.join(script_dir, "sandbox"),
        "../sandbox",
        os.path.join(script_dir, "..", "sandbox"),
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    
    return "./sandbox"  # Default fallback
```

#### 2. Permission Denied

```python
# Error:
PermissionError: [Errno 13] Permission denied: './sandbox'

# Solution:
# Check if file is executable
if not os.access(self.sandbox_path, os.X_OK):
    self.log_output(
        f"❌ Error: Sandbox not executable: {self.sandbox_path}\n" 
        "Run: chmod +x sandbox\n",
        "error"
    )
```

#### 3. Invalid Command

```python
# Error:
execvp() failed: No such file or directory

# Solution in build_command():
if not command:
    self.log_output("❌ Error: No command specified\n", "error")
    return None

# Could add more validation:
if not os.path.exists(command) and not command.startswith('/'):
    self.log_output(
        f"⚠️ Warning: Command not found: {command}\n",
        "warning"
    )
```

#### 4. WSL Not Available

```python
# Error:
FileNotFoundError: [WinError 2] The system cannot find the file specified: 'wsl'

# Solution:
try:
    result = subprocess.run(["wsl", "--version"], capture_output=True)
    if result.returncode != 0:
        self.use_wsl = False
        self.log_output("⚠️ WSL not available, using native mode\n", "warning")
except FileNotFoundError:
    self.use_wsl = False
    self.log_output("⚠️ WSL not installed\n", "warning")
```

---

## 💬 Questions You'll Be Asked

### Q1: "How do you handle output from the sandbox?"

**Answer**:
"We use **subprocess.Popen** with **PIPE** to capture output:

```python
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,  # Capture stdout
    stderr=subprocess.STDOUT  # Merge stderr into stdout
)

# Read line by line
for line in process.stdout:
    output_received.emit(line)  # Send to GUI
```

This gives us:
1. **Real-time streaming**: Output appears as it's generated
2. **Correct ordering**: stderr and stdout properly interleaved
3. **Memory efficient**: Don't accumulate all output before displaying"

### Q2: "Why use threading instead of just calling subprocess.run()?"

**Answer**:
"`subprocess.run()` is **blocking** - it freezes the GUI:

```python
# BAD - GUI freezes
result = subprocess.run(cmd, capture_output=True)
# User can't click anything for 5+ seconds
# Looks like app crashed

# GOOD - GUI stays responsive
executor = CommandExecutor(cmd)
executor.start()
# Returns immediately
# GUI remains interactive
# User can click Stop button
```

Threading is essential for **user experience**."

### Q3: "How does WSL integration work?"

**Answer**:
"WSL allows Windows to run Linux binaries. We detect Windows and prefix commands:

```python
# Windows detection
if platform.system() == 'Windows':
    cmd = ['wsl', './sandbox', ...]  # Wrap with WSL
else:
    cmd = ['./sandbox', ...]  # Direct execution
```

We also convert Windows paths:
```python
'C:\\Users\\file.exe' → '/mnt/c/Users/file.exe'
```

This lets Windows users run our Linux-based sandbox without dual-booting."

### Q4: "What happens if the user stops execution?"

**Answer**:
"We call `process.terminate()` which sends **SIGTERM**:

```python
def stop(self):
    if self.process:
        self.process.terminate()  # Graceful shutdown
        self.process.wait(timeout=5)  # Wait 5 seconds
        
        # If still running:
        if self.process.poll() is None:
            self.process.kill()  # Force kill (SIGKILL)
```

This:
1. Tries graceful shutdown first
2. Gives process time to clean up
3. Force kills if necessary
4. Prevents zombie processes"

### Q5: "How do you prevent double-execution?"

**Answer**:
"We disable the Execute button during execution:

```python
# Before execution:
self.execute_btn.setEnabled(False)  # Disable
self.stop_btn.setEnabled(True)

# Also check:
if self.executor and self.executor.isRunning():
    self.log_output('Execution already in progress', 'warning')
    return
```

This prevents:
- Multiple simultaneous executions
- Resource conflicts
- Confusing output mixing"

### Q6: "What's the benefit of command array vs string?"

**Answer**:
"Arrays are **safer** and **more reliable**:

**String-based** (Bad):
```python
cmd = f\"./sandbox --cpu={cpu} {command}\"
# Problem: What if command has spaces?
# \"./sandbox --cpu=5 /path/with spaces/file\"
# → Breaks into wrong arguments!
```

**Array-based** (Good):
```python
cmd = ['./sandbox', '--cpu=5', '/path/with spaces/file']
# Each element is ONE argument
# No parsing issues!
```

Arrays also prevent **command injection** attacks."

---

## 🎯 Demo Script for Mentor

### 1. Show Command Building
"Let me show how we convert GUI settings to commands..."
```python
# Open zencube_modern_gui.py at build_command()
# Walk through each step:
# - Input validation
# - WSL detection and path conversion
# - Command array construction
# - Limit flag addition
```

### 2. Demonstrate Path Conversion
"On Windows, we need to convert paths for WSL..."
```python
# Show convert_to_wsl_path logic
# Give examples:
print(convert_to_wsl_path("C:\\Users\\test.exe"))
# Output: "/mnt/c/Users/test.exe"
```

### 3. Show Threading in Action
"Threading keeps the GUI responsive..."
```python
# Start a long-running command
# While it's running:
# - Click other buttons (they work!)
# - Resize window (it works!)
# - Click Stop (immediately terminates!)
```

### 4. Demonstrate Output Streaming
"Output appears in real-time, not all at once..."
```python
# Run: ls -lR / (long output)
# Watch output scroll line by line
# Explain: This is line-buffered streaming
```

### 5. Show Error Handling
"We handle errors gracefully..."
```python
# Try invalid command: "notarealcommand"
# Show error message in red
# GUI remains usable
```

---

## ✅ Pre-Presentation Checklist

- [ ] Understand subprocess.Popen thoroughly
- [ ] Know the difference between .run() and .Popen()
- [ ] Can explain PIPE and STDOUT
- [ ] Understand threading vs asyncio
- [ ] Know WSL path conversion algorithm
- [ ] Can explain signal-slot connections
- [ ] Understand line-buffered vs block-buffered
- [ ] Know how to handle process termination
- [ ] Can explain command array vs string
- [ ] Understand exit codes and signals

---

**You're the bridge that makes everything work together! Own it!** 🌉✨
