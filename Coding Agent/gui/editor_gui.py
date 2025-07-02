import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from gui.terminal_gui import AdvancedTerminal 
import subprocess
import threading
import os
import tempfile

def create_editor_panel(self, parent):
    """Create the code editor panel with header controls."""
    # Editor container
    editor_container = ttk.Frame(parent, style="Tertiary.TFrame")
    
    # Editor header with controls
    editor_header = ttk.Frame(editor_container, style="Secondary.TFrame")
    editor_header.pack(fill=tk.X, padx=5, pady=5)
    
    # Left side - Title
    tk.Label(editor_header, text="📝 Code Editor", 
            bg=self.colors["bg_secondary"], 
            fg=self.colors["text_primary"],
            font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT, padx=10, pady=8)
    
    # Right side - Controls
    controls_frame = ttk.Frame(editor_header, style="Secondary.TFrame")
    controls_frame.pack(side=tk.RIGHT, padx=10, pady=5)
    # Terminal toggle button (VS Code style)
    self.terminal_button = ttk.Button(controls_frame, text="🐧", 
                                    style="Terminal.TButton", width=3,
                                    command=self.toggle_terminal)
    self.terminal_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # Language selection
    tk.Label(controls_frame, text="Lang:",
            bg=self.colors["bg_secondary"], 
            fg=self.colors["text_primary"],
            font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 5))
    
    self.language_var = tk.StringVar(value="🐍")
    languages = ["🐍", "☕", "js", "c", "cpp", "go"]
    self.language_combo = ttk.Combobox(controls_frame, textvariable=self.language_var,
                                     values=languages, state="readonly",
                                     style="Modern.TCombobox", width=4)
    self.language_combo.pack(side=tk.LEFT, padx=(0, 10))
    self.language_combo.bind('<<ComboboxSelected>>', self.on_language_change)
    
    # Run button
    self.run_button = ttk.Button(controls_frame, text="▶", 
                               style="Success.TButton", width=3, command=self.run_code)
    self.run_button.pack(side=tk.LEFT, padx=(0, 10))
    
    # Main editor area (will contain editor and terminal)
    self.editor_main = ttk.Frame(editor_container, style="Tertiary.TFrame")
    self.editor_main.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    # Create paned window for editor and terminal
    self.paned_window = ttk.PanedWindow(self.editor_main, orient='vertical')
    self.paned_window.pack(fill=tk.BOTH, expand=True)
    
    # Code editor frame
    create_code_editor(self)
    
    # Create terminal instance (initially hidden)
    create_terminal(self)
    
    # Add to main paned window
    parent.add(editor_container, weight=1)

def create_code_editor(self):
    """Create code editor with line numbers."""
    # Editor frame
    print("Welcome to New Agent Coding Platform")
    editor_frame = tk.Frame(self.paned_window, bg=self.colors["bg_tertiary"])    
    
    # Line numbers
    self.line_numbers = tk.Text(editor_frame, width=4, padx=5, pady=5,
                               font=("Consolas", 11), 
                               bg=self.colors["bg_secondary"],
                               fg=self.colors["text_secondary"],
                               bd=0, state='disabled', wrap='none')
    self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)    
    
    # Code editor
    self.code_editor = scrolledtext.ScrolledText(
        editor_frame,
        wrap=tk.NONE,
        font=("Consolas", 11),
        padx=10, pady=5,
        undo=True, maxundo=50,
        tabs=('1c', '2c', '3c', '4c', '5c', '6c', '7c', '8c')
    )
    self.code_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Bind events for line numbers
    self.code_editor.bind('<KeyRelease>', self.update_line_numbers)
    self.code_editor.bind('<ButtonRelease>', self.update_line_numbers)
    self.code_editor.bind('<MouseWheel>', self.sync_scroll)
    
    # Bind auto-indentation for Python
    self.code_editor.bind('<Return>', self.auto_indent)
    
    # Add to paned window
    self.paned_window.add(editor_frame, weight=3)
    
    # Initial line numbers
    self.update_line_numbers()

def auto_indent(self, event):
    """Auto-indent for Python and other indentation-based languages."""
    lang = self.language_var.get()
    if lang not in ['🐍']:  # Python
        return
        
    # Get current line content
    current_line = self.code_editor.get("insert linestart", "insert")
    
    # Calculate current indentation
    indent = len(current_line) - len(current_line.lstrip())
    
    # Increase indent if line ends with colon
    if current_line.rstrip().endswith(':'):
        indent += 4
        
    # Insert newline and indentation
    self.code_editor.insert(tk.INSERT, '\n' + ' ' * indent)
    
    # Prevent default behavior
    return 'break'

def create_terminal(self):
    """Create the terminal instance."""
    # Create terminal widget but don't add to paned window yet
    self.terminal = AdvancedTerminal(self.paned_window, self.colors)
    self.terminal_frame = self.terminal
    self.terminal_visible = False

def toggle_terminal(self):
    """Toggle the terminal panel visibility (VS Code style)."""
    if self.terminal_visible:
        hide_terminal(self)
    else:
        show_terminal(self)

def show_terminal(self):
    """Show the terminal panel."""
    if not self.terminal_visible:
        self.paned_window.add(self.terminal_frame, weight=1)
        self.terminal_visible = True
        # Update button appearance
        self.terminal_button.configure(text="🐧↓")
        # Set initial position (70% editor, 30% terminal)
        self.root.after(1, lambda: self.paned_window.sashpos(0, int(self.paned_window.winfo_height() * 0.7)))
        # Focus on terminal input
        self.terminal.terminal_input.focus_set()

def hide_terminal(self):
    """Hide the terminal panel."""
    if self.terminal_visible:
        self.paned_window.forget(self.terminal_frame)
        self.terminal_visible = False
        # Update button appearance
        self.terminal_button.configure(text="🐧")

def run_code(self):
    """Execute the code in the editor using the compiler."""
    try:
        # Get code from editor
        code = self.code_editor.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Warning", "No code to execute")
            return
        
        # Get selected language
        lang_symbol = self.language_var.get()
        language_map = {
            "🐍": "python",
            "☕": "java", 
            "js": "javascript",
            "c": "c",
            "cpp": "cpp",
            "go": "go"
        }
        
        language = language_map.get(lang_symbol, "python")
        
        # Show terminal if not visible
        if not self.terminal_visible:
            show_terminal(self)
        
        # Check if compiler is available
        if not hasattr(self, 'compiler'):
            from editor.compiler import CodeCompiler
            self.compiler = CodeCompiler()
        
        # Clear terminal output
        self.terminal.clear_terminal()
        self.terminal.add_output(f"🚀 Running {language.upper()} code...\n", "info")
        
        # Check if code needs user input
        if self.code_needs_input(code, language):
            self.run_interactive_code(code, language)
        else:
            self.run_non_interactive_code(code, language)
            
    except Exception as e:
        if hasattr(self, 'terminal') and self.terminal_visible:
            self.terminal.add_output(f"❌ Error: {str(e)}", "error")
        else:
            messagebox.showerror("Error", f"Failed to execute code: {str(e)}")

def code_needs_input(self, code, language):
    """Check if code contains input statements."""
    input_patterns = {
        "python": ["input(", "raw_input("],
        "java": ["Scanner", "nextLine(", "nextInt(", "next("],
        "c": ["scanf(", "getchar(", "gets("],
        "cpp": ["cin >>", "getline(", "scanf("],
        "go": ["fmt.Scan", "bufio.NewReader"]
    }
    
    patterns = input_patterns.get(language, [])
    return any(pattern in code for pattern in patterns)

def run_interactive_code(self, code, language):
    """Run code that requires user input."""
    try:
        # Create temporary file
        temp_dir = tempfile.mkdtemp()
        file_extensions = {
            "python": ".py",
            "java": ".java", 
            "c": ".c",
            "cpp": ".cpp",
            "go": ".go"
        }
        
        ext = file_extensions.get(language, ".py")
        temp_file = os.path.join(temp_dir, f"main{ext}")
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Get command to run
        commands = {
            "python": ["python3", temp_file],
            "java": self.get_java_command(code, temp_dir),
            "c": self.get_c_command(temp_file, temp_dir),
            "cpp": self.get_cpp_command(temp_file, temp_dir),
            "go": ["go", "run", temp_file]
        }
        
        command = commands.get(language, ["python3", temp_file])
        
        if command:
            # Run interactive process
            self.terminal.run_interactive_process(command, temp_dir)
        
    except Exception as e:
        self.terminal.add_output(f"❌ Error setting up interactive execution: {str(e)}", "error")

def run_non_interactive_code(self, code, language):
    """Run code that doesn't require user input."""
    def execute_in_thread():
        try:
            result = self.compiler.run_code(code, language)
            
            # Display results in terminal
            if result.get("success"):
                if result.get("stdout"):
                    self.terminal.add_output("📤 Output:", "success")
                    self.terminal.add_output(result["stdout"], "output")
                else:
                    self.terminal.add_output("✅ Code executed successfully (no output)", "success")
            else:
                self.terminal.add_output("❌ Execution failed:", "error")
                if result.get("stderr"):
                    self.terminal.add_output(result["stderr"], "error")
                if result.get("error"):
                    self.terminal.add_output(result["error"], "error")
                    
        except Exception as e:
            self.terminal.add_output(f"❌ Execution error: {str(e)}", "error")
    
    # Run in separate thread to avoid blocking UI
    threading.Thread(target=execute_in_thread, daemon=True).start()

def get_java_command(self, code, temp_dir):
    """Get Java compilation and execution command."""
    import re
    class_match = re.search(r'public\s+class\s+(\w+)', code)
    class_name = class_match.group(1) if class_match else "Main"
    
    java_file = os.path.join(temp_dir, f"{class_name}.java")
    with open(java_file, 'w', encoding='utf-8') as f:
        f.write(code)
    
    # Compile first
    compile_result = subprocess.run(["javac", java_file], 
                                  capture_output=True, text=True, cwd=temp_dir)
    if compile_result.returncode != 0:
        raise Exception(f"Java compilation failed: {compile_result.stderr}")
    
    return ["java", "-cp", temp_dir, class_name]

def get_c_command(self, temp_file, temp_dir):
    """Get C compilation and execution command."""
    output_file = os.path.join(temp_dir, "main")
    compile_result = subprocess.run(["gcc", "-o", output_file, temp_file], 
                                  capture_output=True, text=True, cwd=temp_dir)
    if compile_result.returncode != 0:
        raise Exception(f"C compilation failed: {compile_result.stderr}")
    
    return [output_file]

def get_cpp_command(self, temp_file, temp_dir):
    """Get C++ compilation and execution command."""
    output_file = os.path.join(temp_dir, "main")
    compile_result = subprocess.run(["g++", "-o", output_file, temp_file], 
                                  capture_output=True, text=True, cwd=temp_dir)
    if compile_result.returncode != 0:
        raise Exception(f"C++ compilation failed: {compile_result.stderr}")
    
    return [output_file]

def update_line_numbers(self, event=None):
    """Update line numbers in the editor."""
    try:
        # Get the number of lines
        line_count = int(self.code_editor.index('end-1c').split('.')[0])
        
        # Generate line numbers
        line_numbers = '\n'.join(str(i) for i in range(1, line_count + 1))
        
        # Update line numbers display
        self.line_numbers.config(state='normal')
        self.line_numbers.delete(1.0, tk.END)
        self.line_numbers.insert(1.0, line_numbers)
        self.line_numbers.config(state='disabled')
        
    except Exception as e:
        pass  # Ignore errors during line number updates

def sync_scroll(self, event):
    """Synchronize scrolling between editor and line numbers."""
    try:
        # Get the fraction of the editor that's visible
        top, bottom = self.code_editor.yview()
        
        # Apply the same view to line numbers
        self.line_numbers.yview_moveto(top)
        
    except Exception as e:
        pass  # Ignore scrolling errors

def on_language_change(self, event=None):
    """Handle language selection change."""
    try:
        selected_lang = self.language_var.get()
        # You can add language-specific configurations here
        print(f"Language changed to: {selected_lang}")
    except Exception as e:
        pass