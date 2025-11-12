# ROLE 2: GUI Frontend Developer (PySide6 & User Interface)

## 👤 Your Role

You are responsible for the **user interface and user experience** - making ZenCube accessible and intuitive. Your expertise is in Python, Qt framework (PySide6), modern UI design principles, and creating responsive, beautiful interfaces.

---

## 📚 What You Need to Know Inside Out

### Your Primary File: `zencube_modern_gui.py`

**Location**: `zencube/zencube_modern_gui.py`  
**Size**: ~1100 lines  
**Language**: Python 3.8+  
**Framework**: PySide6 (Qt for Python)  
**Purpose**: Modern, responsive GUI for sandbox control

---

## 🎨 Design Philosophy

### Why Modern UI?

**Before (Command Line)**:
```bash
./sandbox --cpu=5 --mem=256 --procs=10 /bin/ls -la
```
❌ Intimidating for non-technical users  
❌ Easy to make syntax errors  
❌ No visual feedback  
❌ Hard to remember all options  

**After (GUI)**:
- ✅ Visual controls with labels
- ✅ Instant validation
- ✅ Real-time output display
- ✅ Quick command presets
- ✅ Beautiful, modern design

### Design Principles

1. **React-Inspired**: Component-based architecture
2. **Material Design**: Cards, shadows, rounded corners
3. **Responsive**: Adapts to different window sizes
4. **Accessible**: Clear labels, logical grouping
5. **Intuitive**: No manual required

---

## 🏗️ Architecture Overview

### Component Hierarchy

```
ZenCubeModernGUI (QMainWindow)
├── Header (ModernCard)
│   ├── Title + Subtitle
│   └── Settings Button
│
├── Splitter (QSplitter - resizable)
│   │
│   ├── TOP SECTION (Scroll Area)
│   │   ├── Command Selection (ModernCard)
│   │   │   ├── Command Input (ModernInput)
│   │   │   ├── Browse Button
│   │   │   ├── Arguments Input
│   │   │   └── Quick Commands (FlowLayout)
│   │   │       ├── ls button
│   │   │       ├── echo button
│   │   │       ├── whoami button
│   │   │       └── Test buttons
│   │   │
│   │   └── Resource Limits (ModernCard)
│   │       ├── CPU Checkbox + SpinBox
│   │       ├── Memory Checkbox + SpinBox
│   │       ├── Processes Checkbox + SpinBox
│   │       ├── File Size Checkbox + SpinBox
│   │       ├── Preset Buttons (FlowLayout)
│   │       └── WSL Checkbox
│   │
│   └── BOTTOM SECTION
│       └── Terminal Output (ModernCard)
│           └── Output Text (QTextEdit)
│
├── Control Buttons (FlowLayout)
│   ├── Execute Button (Primary)
│   ├── Stop Button
│   ├── Clear Button
│   ├── Toggle Terminal Button
│   └── Help Button
│
└── Status Bar
    └── System information
```

---

## 🔧 Custom Components Deep Dive

### 1. FlowLayout (Lines 36-110)

**Purpose**: Responsive layout that wraps widgets like CSS flexbox

#### Why We Need It:

**Standard Qt Layouts**:
- `QHBoxLayout`: Horizontal (never wraps)
- `QVBoxLayout`: Vertical (never wraps)
- `QGridLayout`: Fixed grid (not responsive)

**FlowLayout**:
- Wraps to next line when width runs out
- Perfect for buttons that should adapt to window size

#### Implementation:

```python
class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing if spacing >= 0 else 10)
        self.item_list = []  # List of layout items
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def heightForWidth(self, width):
        # Calculate required height for given width
        return self._do_layout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)
```

**Key Method**: `_do_layout()`
```python
def _do_layout(self, rect, test_only):
    x = rect.x()
    y = rect.y()
    line_height = 0
    
    for item in self.item_list:
        widget = item.widget()
        space_x = self.spacing()
        
        next_x = x + widget.sizeHint().width() + space_x
        
        if next_x - space_x > rect.right() and line_height > 0:
            # Doesn't fit on current line → wrap to next line
            x = rect.x()
            y = y + line_height + space_x
            next_x = x + widget.sizeHint().width() + space_x
            line_height = 0
        
        if not test_only:
            widget.setGeometry(QRect(QPoint(x, y), widget.sizeHint()))
        
        x = next_x
        line_height = max(line_height, widget.sizeHint().height())
    
    return y + line_height - rect.y()
```

**Visual Example**:
```
Wide Window (800px):
┌────────────────────────────────────────────────────┐
│ [Button1] [Button2] [Button3] [Button4] [Button5] │
└────────────────────────────────────────────────────┘

Narrow Window (400px):
┌─────────────────────────┐
│ [Button1] [Button2]     │
│ [Button3] [Button4]     │
│ [Button5]               │
└─────────────────────────┘
```

---

### 2. ModernButton (Lines 113-175)

**Purpose**: Styled button with gradient, shadows, and hover effects

#### Styling:

```python
class ModernButton(QPushButton):
    def __init__(self, text, primary=False, parent=None):
        super().__init__(text, parent)
        self.primary = primary
        self.setMinimumHeight(35)
        self.setCursor(Qt.PointingHandCursor)  # Hand cursor on hover
        self._setup_style()
```

**Primary Button** (Execute):
```css
QPushButton {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #667eea,    /* Purple-blue */
        stop:1 #764ba2     /* Deep purple */
    );
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 24px;
    font-weight: 600;
    font-size: 14px;
}

QPushButton:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #5568d3,    /* Darker on hover */
        stop:1 #653a8f
    );
}

QPushButton:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:1,
        stop:0 #4c5abd,    /* Even darker when pressed */
        stop:1 #563280
    );
}
```

**Secondary Button** (Clear, Help):
```css
QPushButton {
    background-color: white;
    color: #4a5568;
    border: 2px solid #e2e8f0;
    border-radius: 8px;
    /* ... */
}
```

**Shadow Effect**:
```python
shadow = QGraphicsDropShadowEffect()
shadow.setBlurRadius(15)           # How blurred the shadow is
shadow.setColor(QColor(0, 0, 0, 40))  # Semi-transparent black
shadow.setOffset(0, 4)             # 4px down
self.setGraphicsEffect(shadow)
```

---

### 3. ModernCard (Lines 178-208)

**Purpose**: Container with white background, rounded corners, shadow

#### Implementation:

```python
class ModernCard(QFrame):
    def __init__(self, title=None, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        
        # Card styling
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)
        
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Optional title
        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #2d3748;
                margin-bottom: 10px;
            """)
            self.main_layout.addWidget(title_label)
```

**Visual Effect**:
```
┌─────────────────────────────────┐
│  Card Title                     │  ← Bold, dark text
│  ─────────────────────────      │
│                                 │
│  [Content goes here]            │
│                                 │
└─────────────────────────────────┘
  └─ Subtle shadow for depth
```

---

### 4. ModernInput (Lines 211-233)

**Purpose**: Styled text input with focus effects

```python
class ModernInput(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setMinimumHeight(36)
        
        self.setStyleSheet("""
            QLineEdit {
                background-color: #f7fafc;      /* Light gray background */
                border: 2px solid #e2e8f0;      /* Light border */
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                color: #2d3748;
            }
            QLineEdit:focus {
                border-color: #667eea;          /* Blue when focused */
                background-color: white;
            }
            QLineEdit:hover {
                border-color: #cbd5e0;          /* Darker border on hover */
            }
        """)
```

**States**:
- **Normal**: Light gray background, gray border
- **Hover**: Slightly darker border
- **Focus**: White background, blue border (shows user where they're typing)

---

### 5. ModernCheckbox (Lines 236-260)

**Purpose**: Custom-styled checkbox with gradient when checked

```python
class ModernCheckbox(QCheckBox):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #2d3748;
                spacing: 10px;
            }
            
            QCheckBox::indicator {
                width: 24px;
                height: 24px;
                border-radius: 6px;
                border: 2px solid #cbd5e0;
                background: white;
            }
            
            QCheckBox::indicator:checked {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
                border-color: #667eea;
            }
        """)
```

**Visual States**:
```
Unchecked: [ ] CPU Time Limit
Checked:   [✓] CPU Time Limit  (gradient purple)
```

---

### 6. ModernSpinBox (Lines 263-300)

**Purpose**: Number input with +/- buttons

```python
class ModernSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(36)
        
        self.setStyleSheet("""
            QSpinBox {
                background-color: #f7fafc;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
            }
            
            QSpinBox::up-button, QSpinBox::down-button {
                width: 30px;
                border-radius: 4px;
                background: #e2e8f0;
            }
            
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background: #cbd5e0;
            }
        """)
```

**Visual**:
```
┌─────────────────────────┐
│  256        [▲]  [▼]   │  ← Up/Down buttons
└─────────────────────────┘
```

---

## 🧵 Threading: CommandExecutor (Lines 303-342)

### Why Threading?

**Without Threading** (Bad):
```python
# This blocks the GUI!
process = subprocess.run(["./sandbox", "--cpu=5", "./infinite_loop"])
# GUI freezes for 5+ seconds
# User can't click anything
# Looks like app crashed
```

**With Threading** (Good):
```python
# Runs in separate thread
executor = CommandExecutor(command_parts)
executor.output_received.connect(self.log_output)  # Updates GUI asynchronously
executor.start()
# GUI remains responsive
# User can click Stop button
```

### Implementation:

```python
class CommandExecutor(QThread):
    # Signals for communication with GUI
    output_received = Signal(str)    # Emitted when output line received
    finished_signal = Signal(int)    # Emitted when process finishes
    
    def __init__(self, command_parts):
        super().__init__()
        self.command_parts = command_parts  # ["./sandbox", "--cpu=5", ...]
        self.process = None
    
    def run(self):
        """This method runs in a separate thread"""
        try:
            self.process = subprocess.Popen(
                self.command_parts,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                text=True,                 # Decode bytes to string
                bufsize=1                  # Line-buffered
            )
            
            # Stream output line by line
            for line in self.process.stdout:
                self.output_received.emit(line)  # Send to GUI
            
            # Wait for process to finish
            exit_code = self.process.wait()
            self.finished_signal.emit(exit_code)
            
        except Exception as e:
            self.output_received.emit(f"Error: {str(e)}\n")
            self.finished_signal.emit(-1)
    
    def stop(self):
        """Stop the running process"""
        if self.process:
            self.process.terminate()  # Send SIGTERM
            self.process.wait(timeout=5)
```

### Signal-Slot Mechanism:

```python
# In ZenCubeModernGUI.execute_command():
self.executor = CommandExecutor(cmd_parts)

# Connect signals to methods
self.executor.output_received.connect(self.log_output)
self.executor.finished_signal.connect(self.on_command_finished)

# Start thread
self.executor.start()
```

**Flow**:
```
Thread (CommandExecutor)          Main Thread (GUI)
────────────────────────          ─────────────────
run() starts
  ↓
subprocess.Popen()
  ↓
for line in stdout:
  output_received.emit(line) ────→ log_output(line)
                                    ↓
                                    Update QTextEdit
  ↓
process.wait()
  ↓
finished_signal.emit(code) ──────→ on_command_finished(code)
                                    ↓
                                    Re-enable buttons
```

---

## 🎨 Main Window: ZenCubeModernGUI (Lines 346-1075)

### Initialization (Lines 348-367)

```python
class ZenCubeModernGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # State variables
        self.executor = None                           # Current thread
        self.use_wsl = platform.system() == "Windows"  # Auto-detect WSL
        self.sandbox_path = self.detect_sandbox_path() # Find sandbox binary
        self.terminal_visible = True                   # Terminal toggle state
        
        # Window setup
        self.setWindowTitle("ZenCube Sandbox - Modern UI")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 750)
        
        # Build UI
        self.setup_ui()
        self.apply_theme()
        self.center_window()
```

---

### Command Section (Lines 536-596)

**Purpose**: Let user select command to execute

#### Components:

1. **Command Input**:
```python
self.command_input = ModernInput("Enter command or browse...")
```
- User types command path: `/bin/ls`, `./tests/infinite_loop`
- Or uses browse button

2. **Browse Button**:
```python
browse_btn = ModernButton("📁 Browse")
browse_btn.clicked.connect(self.browse_file)
```
Opens file dialog to select executable

3. **Arguments Input**:
```python
self.args_input = ModernInput("Optional arguments...")
```
User enters command-line arguments: `-la`, `--help`

4. **Quick Commands**:
```python
quick_commands = [
    ("📋 ls", "/bin/ls", "-la"),
    ("💬 echo", "/bin/echo", "Hello ZenCube!"),
    ("👤 whoami", "/usr/bin/whoami", ""),
    ("⏱️ CPU Test", "./tests/infinite_loop", ""),
    ("💾 Memory Test", "./tests/memory_hog", ""),
]

for label, cmd, args in quick_commands:
    btn = ModernButton(label)
    btn.clicked.connect(lambda c=cmd, a=args: self.set_quick_command(c, a))
    quick_layout.addWidget(btn)
```

**Why lambda?**
```python
# WRONG - all buttons would use last value
btn.clicked.connect(lambda: self.set_quick_command(cmd, args))

# CORRECT - captures current value
btn.clicked.connect(lambda c=cmd, a=args: self.set_quick_command(c, a))
```

---

### Limits Section (Lines 598-685)

**Purpose**: Configure resource limits

#### Grid Layout:

```python
grid = QGridLayout()

# CPU Limit
self.cpu_check = ModernCheckbox("CPU Time (sec)")
self.cpu_spin = ModernSpinBox()
self.cpu_spin.setRange(1, 3600)
self.cpu_spin.setValue(5)
self.cpu_spin.setEnabled(False)  # Disabled until checkbox checked

# Connect checkbox to spinbox
self.cpu_check.toggled.connect(lambda checked: self.cpu_spin.setEnabled(checked))

grid.addWidget(self.cpu_check, 0, 0)  # Row 0, Column 0
grid.addWidget(self.cpu_spin, 0, 1)   # Row 0, Column 1
```

**Grid Layout**:
```
Row 0:  [CPU Checkbox]  [CPU SpinBox]  [Mem Checkbox]  [Mem SpinBox]
Row 1:  [Proc Checkbox] [Proc SpinBox] [File Checkbox] [File SpinBox]
```

#### Preset Buttons:

```python
presets = [
    ("🔓 No Limits", self.preset_none),
    ("🟢 Light", self.preset_light),
    ("🟡 Medium", self.preset_medium),
    ("🔴 Strict", self.preset_strict),
]

for label, func in presets:
    btn = ModernButton(label)
    btn.clicked.connect(func)
    preset_layout.addWidget(btn)
```

**Preset Functions**:
```python
def preset_strict(self):
    """Enable all limits with strict values"""
    self.cpu_check.setChecked(True)
    self.cpu_spin.setValue(5)
    
    self.mem_check.setChecked(True)
    self.mem_spin.setValue(256)
    
    self.procs_check.setChecked(True)
    self.procs_spin.setValue(5)
    
    self.fsize_check.setChecked(True)
    self.fsize_spin.setValue(50)
    
    self.log_output("📋 Preset: Strict (All limits enabled)\n", "info")
```

---

### Output Section (Lines 687-722)

**Purpose**: Display command output in terminal-style

```python
self.output_text = QTextEdit()
self.output_text.setReadOnly(True)  # User can't edit
self.output_text.setMinimumHeight(150)

self.output_text.setStyleSheet("""
    QTextEdit {
        background-color: #1a202c;  /* Dark background */
        color: #00ff00;             /* Green text (terminal style) */
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        padding: 15px;
    }
""")

# Initial welcome message
self.log_output("🧊 ZenCube Sandbox Terminal\n", "info")
self.log_output("=" * 80 + "\n", "info")
self.log_output("Ready to execute commands.\n\n", "success")
```

#### Color-Coded Output:

```python
def log_output(self, message, msg_type=None):
    """Add message to output with color coding"""
    cursor = self.output_text.textCursor()
    cursor.movePosition(QTextCursor.End)
    
    # Set color based on message type
    if msg_type == "error":
        cursor.insertHtml(f'<span style="color: #ff6b6b;">{message}</span>')
    elif msg_type == "success":
        cursor.insertHtml(f'<span style="color: #51cf66;">{message}</span>')
    elif msg_type == "warning":
        cursor.insertHtml(f'<span style="color: #ffd93d;">{message}</span>')
    elif msg_type == "info":
        cursor.insertHtml(f'<span style="color: #74c0fc;">{message}</span>')
    else:
        cursor.insertText(message)
    
    # Auto-scroll to bottom
    self.output_text.setTextCursor(cursor)
    self.output_text.ensureCursorVisible()
```

---

### Control Buttons (Lines 724-763)

```python
def create_control_buttons(self, layout):
    button_layout = FlowLayout(spacing=15)
    
    # Execute button (primary action)
    self.execute_btn = ModernButton("▶️ Execute Command", primary=True)
    self.execute_btn.clicked.connect(self.execute_command)
    
    # Stop button (disabled initially)
    self.stop_btn = ModernButton("⏹️ Stop")
    self.stop_btn.setEnabled(False)
    self.stop_btn.clicked.connect(self.stop_execution)
    
    # Clear output button
    clear_btn = ModernButton("🗑️ Clear")
    clear_btn.clicked.connect(self.clear_output)
    
    # Toggle terminal visibility
    self.toggle_terminal_btn = ModernButton("👁️ Hide Terminal")
    self.toggle_terminal_btn.clicked.connect(self.toggle_terminal)
    
    # Help dialog
    help_btn = ModernButton("❓ Help")
    help_btn.clicked.connect(self.show_help)
```

**Button States During Execution**:
```python
# When execution starts:
self.execute_btn.setEnabled(False)  # Disable to prevent double-execution
self.stop_btn.setEnabled(True)      # Enable stop button

# When execution finishes:
self.execute_btn.setEnabled(True)   # Re-enable execute
self.stop_btn.setEnabled(False)     # Disable stop
```

---

## 🚀 Key Methods Explained

### execute_command() (Lines 934-967)

**Purpose**: Build command and start execution

```python
def execute_command(self):
    try:
        # Build command array
        cmd_parts = self.build_command()
        if not cmd_parts:
            return  # Validation failed
        
        # Clear previous output
        self.clear_output()
        
        # Log the command
        self.log_output("=" * 80 + "\n", "info")
        self.log_output("🚀 Executing Command\n", "info")
        self.log_output(f"Command: {' '.join(cmd_parts)}\n", "info")
        self.log_output("=" * 80 + "\n\n", "info")
        
        # Update button states
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Create and start executor thread
        self.executor = CommandExecutor(cmd_parts)
        self.executor.output_received.connect(
            lambda msg: self.log_output(msg)
        )
        self.executor.finished_signal.connect(self.on_command_finished)
        self.executor.start()
        
    except Exception as e:
        self.log_output(f"❌ Error: {str(e)}\n", "error")
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
```

### build_command() (Lines 893-930)

**Purpose**: Convert GUI state to command array

```python
def build_command(self):
    command = self.command_input.text().strip()
    args = self.args_input.text().strip()
    
    if not command:
        self.log_output("❌ Error: No command specified\n", "error")
        return None
    
    # Handle WSL
    if self.use_wsl:
        # Convert Windows path to WSL path if needed
        if ':' in command:
            drive = command[0].lower()
            path = command[2:].replace('\\', '/')
            command = f"/mnt/{drive}{path}"
        
        cmd_parts = ["wsl", "./sandbox"]
    else:
        cmd_parts = ["./sandbox"]
    
    # Add resource limits
    if self.cpu_check.isChecked():
        cmd_parts.append(f"--cpu={self.cpu_spin.value()}")
    
    if self.mem_check.isChecked():
        cmd_parts.append(f"--mem={self.mem_spin.value()}")
    
    if self.procs_check.isChecked():
        cmd_parts.append(f"--procs={self.procs_spin.value()}")
    
    if self.fsize_check.isChecked():
        cmd_parts.append(f"--fsize={self.fsize_spin.value()}")
    
    # Add command and arguments
    cmd_parts.append(command)
    if args:
        cmd_parts.extend(args.split())
    
    return cmd_parts
```

**Example Output**:
```python
# GUI state:
# - Command: ./tests/infinite_loop
# - CPU: Checked, 5 seconds
# - Memory: Checked, 256 MB
# - Processes: Unchecked
# - Arguments: (empty)

# Result:
["./sandbox", "--cpu=5", "--mem=256", "./tests/infinite_loop"]
```

### toggle_terminal() (Lines 995-1011)

**Purpose**: Show/hide terminal output to save space

```python
def toggle_terminal(self):
    if self.terminal_visible:
        # Hide terminal
        self.bottom_widget.hide()
        self.toggle_terminal_btn.setText("👁️ Show Terminal")
        self.terminal_visible = False
    else:
        # Show terminal
        self.bottom_widget.show()
        self.toggle_terminal_btn.setText("👁️ Hide Terminal")
        self.terminal_visible = True
```

---

## 🎨 Styling & Theme

### Application-Wide Theme (Lines 773-807)

```python
def apply_theme(self):
    self.setStyleSheet("""
        QMainWindow {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:1,
                stop:0 #f7fafc,  /* Light gray */
                stop:1 #edf2f7   /* Lighter gray */
            );
        }
        
        QWidget {
            font-family: -apple-system, BlinkMacSystemFont, 
                'Segoe UI', 'Roboto', sans-serif;
        }
        
        QScrollBar:vertical {
            background: #e2e8f0;
            width: 10px;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical {
            background: #cbd5e0;
            border-radius: 5px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #a0aec0;
        }
    """)
```

### Color Palette:

```python
# Primary Colors
PURPLE_BLUE = "#667eea"      # Main accent
DEEP_PURPLE = "#764ba2"      # Secondary accent

# Grays (Light to Dark)
GRAY_50 = "#f7fafc"          # Lightest (background)
GRAY_100 = "#edf2f7"
GRAY_200 = "#e2e8f0"         # Borders
GRAY_300 = "#cbd5e0"
GRAY_400 = "#a0aec0"
GRAY_500 = "#718096"         # Secondary text
GRAY_600 = "#4a5568"         # Body text
GRAY_700 = "#2d3748"         # Headings
GRAY_800 = "#1a202c"         # Terminal background

# Status Colors
SUCCESS_GREEN = "#51cf66"
ERROR_RED = "#ff6b6b"
WARNING_YELLOW = "#ffd93d"
INFO_BLUE = "#74c0fc"
```

---

## 💬 Questions You'll Be Asked

### Q1: "Why use PySide6 instead of Tkinter?"

**Answer**:
"PySide6 (Qt) is more powerful than Tkinter:

1. **Better styling**: Qt StyleSheets (CSS-like) vs Tkinter's limited styling
2. **Modern widgets**: Built-in support for shadows, gradients, animations
3. **Cross-platform**: Looks native on Windows, Mac, Linux
4. **Threading**: QThread is safer than Tkinter's threading
5. **Professional**: Used in industry (Maya, Spotify, VLC)

Tkinter is great for simple apps, but ZenCube needs a polished, modern UI."

### Q2: "How does the GUI communicate with the C sandbox?"

**Answer**:
"The GUI uses **subprocess** to execute the sandbox binary:

```python
# Build command array
cmd = ["./sandbox", "--cpu=5", "--mem=256", "/bin/ls"]

# Execute using subprocess
process = subprocess.Popen(
    cmd,
    stdout=subprocess.PIPE,  # Capture output
    stderr=subprocess.STDOUT # Merge errors into output
)

# Read output line by line
for line in process.stdout:
    print(line)  # Display in GUI
```

The C program doesn't know it's being called by a GUI - it just runs like a normal command-line program."

### Q3: "Why use threading instead of async/await?"

**Answer**:
"Qt's event loop conflicts with Python's asyncio. QThread is Qt's native solution:

**Advantages of QThread**:
- Integrates perfectly with Qt signals/slots
- No event loop conflicts
- Easy to cancel (process.terminate())
- Qt handles thread safety automatically

**If we used asyncio**:
- Would need to integrate two event loops (Qt + asyncio)
- More complex with QAsyncio
- QThread is simpler and works out of the box"

### Q4: "What's the benefit of the FlowLayout?"

**Answer**:
"FlowLayout makes the GUI **responsive** without media queries:

**Problem**: Standard layouts don't wrap:
```
Wide: [Btn1] [Btn2] [Btn3] [Btn4] [Btn5]
Narrow: [Btn1] [Btn2] [Btn3] [...] ← Buttons cut off!
```

**Solution**: FlowLayout wraps automatically:
```
Wide: [Btn1] [Btn2] [Btn3] [Btn4] [Btn5]
Narrow: [Btn1] [Btn2] [Btn3]
        [Btn4] [Btn5]
```

It's like CSS flexbox with `flex-wrap: wrap` - essential for modern responsive design."

### Q5: "How do you ensure the GUI doesn't freeze?"

**Answer**:
"Three techniques:

1. **Threading**: Long operations (sandbox execution) run in QThread
2. **Signals**: Thread communicates with GUI using signals (thread-safe)
3. **Event processing**: GUI event loop keeps running while thread works

**Without threading**:
```python
process.wait()  # Blocks GUI for 5+ seconds
# User thinks app crashed
```

**With threading**:
```python
executor.start()  # Returns immediately
# GUI remains responsive
# User can click Stop button
```"

### Q6: "Why use cards instead of a flat layout?"

**Answer**:
"Card-based design improves **visual hierarchy** and **organization**:

**Benefits**:
1. **Grouping**: Related controls grouped visually
2. **Focus**: Shadows create depth, draw attention
3. **Modern**: Used by Google (Material), Apple (iOS)
4. **Readable**: White cards on gray background reduce eye strain
5. **Scannable**: Users quickly find sections

Compare:
```
Without Cards:          With Cards:
┌───────────────────┐   ┌─────────────────┐ ← Shadow
│ Everything flat   │   │ Command Section │
│ Hard to scan      │   └─────────────────┘
│                   │   ┌─────────────────┐
│                   │   │ Limits Section  │
└───────────────────┘   └─────────────────┘
                        Clear separation!
```"

---

## 🎯 Demo Script for Mentor

### 1. Show UI Overview
"Let me walk you through the interface..."
- Point to header: "Title and settings"
- Point to command section: "Where users select what to run"
- Point to limits: "Configure resource restrictions"
- Point to terminal: "Real-time output"
- Point to controls: "Execute, stop, clear, toggle, help"

### 2. Demonstrate Responsiveness
- Resize window narrow → Show buttons wrapping
- Resize window wide → Show buttons in one line
- Drag splitter → Show terminal resizing

### 3. Show Quick Commands
"For ease of use, we provide preset commands..."
- Click "📋 ls" → Show how it fills command field
- Click "⏱️ CPU Test" → Show test program selection

### 4. Demonstrate Presets
"Resource limit presets for common scenarios..."
- Click "🔓 No Limits" → Show all unchecked
- Click "🔴 Strict" → Show all limits enabled
- Explain use cases for each

### 5. Live Execution
"Now let's execute a command..."
- Select "⏱️ CPU Test"
- Set CPU limit to 5 seconds
- Click Execute
- **Point out**: "Notice the GUI is still responsive during execution"
- Show output streaming in real-time
- Wait for SIGXCPU
- Point out colored error message

### 6. Show Threading
"The GUI stays responsive because we use threading..."
- Start another execution
- While running, try clicking buttons
- Click Stop → Show instant termination
- Explain QThread and signals

### 7. Toggle Terminal
"For space, users can hide the terminal..."
- Click "Hide Terminal" → Show it disappear
- Click "Show Terminal" → Show it reappear

---

## ✅ Pre-Presentation Checklist

- [ ] Run GUI successfully: `python zencube_modern_gui.py`
- [ ] Test all quick commands
- [ ] Test all presets
- [ ] Test execute, stop, clear buttons
- [ ] Test terminal toggle
- [ ] Test window resizing (responsiveness)
- [ ] Know exact line numbers of key components
- [ ] Practice explaining FlowLayout
- [ ] Practice explaining QThread/Signals
- [ ] Prepare to show responsive design

---

**You've built a beautiful, functional interface! Show it with pride!** 🎨✨
