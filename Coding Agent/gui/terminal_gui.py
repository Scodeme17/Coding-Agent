import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import shlex
import platform
import socket
from datetime import datetime
from typing import Callable, Optional, Dict, Any
import time
import queue

class AdvancedTerminal(ttk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent)
        self.parent = parent
        self.colors = colors
        
        # Initialize missing attributes
        self.current_directory = os.getcwd()
        self.command_history = []
        self.history_index = -1
        
        # Process management
        self.current_process = None
        self.output_queue = queue.Queue()
        
        # Animation state
        self.is_processing = False
        self.animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.animation_index = 0
        
        # Widget destruction flag
        self.is_destroyed = False
        
        # Setup UI
        self.setup_ui()
        
        # Start output processor
        self.process_output()
        
        # Initial welcome message
        self.after(100, self.show_welcome)

    def setup_ui(self):
        """Create terminal UI components."""
        # Configure this frame
        self.configure(style="Tertiary.TFrame")
        
        # Terminal header
        terminal_header = ttk.Frame(self, style="Secondary.TFrame")
        terminal_header.pack(fill=tk.X, padx=2, pady=2)
        
        # Terminal title with animated icon
        self.title_frame = tk.Frame(terminal_header, bg=self.colors["bg_secondary"])
        self.title_frame.pack(side=tk.LEFT, padx=8, pady=4)
        
        self.icon_label = tk.Label(self.title_frame, text="🐧", 
                                  bg=self.colors["bg_secondary"], 
                                  fg=self.colors["text_primary"],
                                  font=("Segoe UI", 12))
        self.icon_label.pack(side=tk.LEFT)
        
        self.title_label = tk.Label(self.title_frame, text=" Terminal", 
                                   bg=self.colors["bg_secondary"], 
                                   fg=self.colors["text_primary"],
                                   font=("Segoe UI", 10, "bold"))
        self.title_label.pack(side=tk.LEFT)
        
        # Status indicators
        status_frame = tk.Frame(terminal_header, bg=self.colors["bg_secondary"])
        status_frame.pack(side=tk.LEFT, padx=20)
        
        self.status_icon = tk.Label(status_frame, text="●", 
                                   bg=self.colors["bg_secondary"], 
                                   fg=self.colors["success"],
                                   font=("Segoe UI", 10))
        self.status_icon.pack(side=tk.LEFT)
        
        self.status_text = tk.Label(status_frame, text="Ready", 
                                   bg=self.colors["bg_secondary"], 
                                   fg=self.colors["success"],
                                   font=("Segoe UI", 9))
        self.status_text.pack(side=tk.LEFT, padx=(5, 0))
        
        # Terminal controls
        terminal_controls = tk.Frame(terminal_header, bg=self.colors["bg_secondary"])
        terminal_controls.pack(side=tk.RIGHT, padx=8, pady=2)
        
        clear_btn = tk.Button(terminal_controls, text="🧹", 
                             command=self.clear_terminal,
                             bg=self.colors["bg_tertiary"],
                             fg=self.colors["text_primary"],
                             relief=tk.FLAT,
                             width=3,
                             font=("Segoe UI", 10))
        clear_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Close terminal button - Fixed callback
        close_btn = tk.Button(terminal_controls, text="🗑️", 
                             command=self.hide_terminal,  # Fixed: removed parentheses
                             bg=self.colors["error"],
                             fg="white",
                             relief=tk.FLAT,
                             width=3,
                             font=("Segoe UI", 10, "bold"))
        close_btn.pack(side=tk.RIGHT)
        
        # Terminal output area
        output_frame = tk.Frame(self, bg=self.colors["bg_tertiary"])
        output_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Create terminal output with custom scrollbar
        self.terminal_output = tk.Text(
            output_frame,
            wrap=tk.WORD,
            font=("JetBrains Mono", 10) if self.font_available("JetBrains Mono") else ("Consolas", 10),
            height=12,
            state='normal',
            bg="#0c0c0c",
            fg="#00ff00",  # Green terminal text
            insertbackground="#00ff00",
            selectbackground=self.colors["accent"],
            selectforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=10,
            pady=5
        )
        
        # Custom scrollbar
        scrollbar = tk.Scrollbar(output_frame, command=self.terminal_output.yview,
                                bg=self.colors["bg_secondary"],
                                troughcolor=self.colors["bg_tertiary"],
                                activebackground=self.colors["accent"])
        self.terminal_output.configure(yscrollcommand=scrollbar.set)
        
        # Pack terminal and scrollbar
        self.terminal_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure text tags for colored output
        self.setup_text_tags()
        
        # Command input area
        self.create_command_input()
        
    def font_available(self, font_name):
        """Check if a font is available."""
        try:
            import tkinter.font as tkFont
            return font_name in tkFont.families()
        except:
            return False
    
    def setup_text_tags(self):
        """Setup colored text tags for terminal output."""
        self.terminal_output.tag_configure("prompt", foreground="#00ff00", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("path", foreground="#0080ff", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("user", foreground="#ffff00", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("timestamp", foreground="#888888", font=("Consolas", 9))
        self.terminal_output.tag_configure("info", foreground="#cccccc")
        self.terminal_output.tag_configure("success", foreground="#00ff00", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("warning", foreground="#ffaa00", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("error", foreground="#ff4444", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("command", foreground="#88aaff", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("output", foreground="#dddddd")
        self.terminal_output.tag_configure("system", foreground="#ff88ff", font=("Consolas", 10, "bold"))
        self.terminal_output.tag_configure("input", foreground="#00ffff", font=("Consolas", 10, "bold"))

    def create_command_input(self):
        """Create the command input area."""
        input_frame = tk.Frame(self, bg=self.colors["bg_tertiary"])
        input_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        # Create prompt display
        self.prompt_frame = tk.Frame(input_frame, bg="#0c0c0c")
        self.prompt_frame.pack(fill=tk.X, pady=0)
        
        
        self.prompt_label = tk.Label(
            self.prompt_frame,
            bg="#0c0c0c",
            fg="#00ff00",
            font=("JetBrains Mono", 10, "bold") if self.font_available("JetBrains Mono") else ("Consolas", 10, "bold"),
            anchor="w"
        )
        self.update_prompt()
        
        # Command input
        self.terminal_input = tk.Entry(
            input_frame,
            bg="#0c0c0c",
            fg="#00ff00",
            insertbackground="#00ff00",
            font=("JetBrains Mono", 10) if self.font_available("JetBrains Mono") else ("Consolas", 10),
            relief=tk.FLAT,
            borderwidth=1,
            highlightthickness=2,
            highlightcolor="#00ff00",
            highlightbackground="#333333"
        )
        self.terminal_input.pack(fill=tk.X, padx=8, pady=3)
        self.terminal_input.bind("<Return>", self.execute_command)
        self.terminal_input.bind("<Tab>", self.tab_completion)
        self.terminal_input.bind("<Control-c>", self.interrupt_command)
        # Focus on input
        self.terminal_input.focus_set()

    def update_prompt(self):
        """Update the command prompt display."""
        user = os.getenv('USER', os.getenv('USERNAME', 'user'))
        hostname = socket.gethostname()
        current_dir = os.path.basename(self.current_directory) or self.current_directory
        prompt_text = f"{user}@{hostname}:{current_dir}$"
        self.prompt_label.config(text=prompt_text)

    def show_welcome(self):
        """Show welcome message."""
        if not self.is_destroyed:
            self.add_output(f"Terminal initialized - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "info")

    def add_output(self, text, tag="info", newline=True):
        """Add text to terminal output."""
        if self.is_destroyed:
            return
            
        try:
            self.terminal_output.config(state='normal')
            
            if newline and text:
                text += "\n"
                
            self.terminal_output.insert(tk.END, text, tag)
            self.terminal_output.see(tk.END)
            self.terminal_output.config(state='disabled')
        except tk.TclError:
            # Widget has been destroyed
            self.is_destroyed = True

    def clear_terminal(self):
        """Clear the terminal output."""
        if self.is_destroyed:
            return
            
        try:
            self.terminal_output.config(state='normal')
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_output.config(state='disabled')
            self.add_output("Terminal cleared 🧹", "info")
        except tk.TclError:
            self.is_destroyed = True

    def tab_completion(self, event):
        """Handle tab completion."""
        current_text = self.terminal_input.get()
        cursor_pos = self.terminal_input.index(tk.INSERT)
        
        # Simple file/directory completion
        if current_text:
            try:
                parts = current_text.split()
                if parts:
                    last_part = parts[-1]
                    directory = os.path.dirname(last_part) or self.current_directory
                    prefix = os.path.basename(last_part)
                    
                    matches = []
                    try:
                        for item in os.listdir(directory):
                            if item.startswith(prefix):
                                matches.append(item)
                    except (OSError, PermissionError):
                        pass
                    
                    if len(matches) == 1:
                        # Single match - complete it
                        full_path = os.path.join(directory, matches[0])
                        if os.path.isdir(full_path):
                            matches[0] += "/"
                        
                        new_text = current_text[:current_text.rfind(prefix)] + matches[0]
                        self.terminal_input.delete(0, tk.END)
                        self.terminal_input.insert(0, new_text)
                    elif len(matches) > 1:
                        # Multiple matches - show them
                        self.add_output(f"Completions: {' '.join(matches)}", "info")
            except Exception:
                pass
        
        return "break"

    def interrupt_command(self, event):
        """Handle Ctrl+C to interrupt current command."""
        if self.current_process:
            try:
                self.current_process.terminate()
                self.add_output("^C", "warning")
                self.add_output("Process interrupted", "warning")
                self.stop_animation()
            except Exception:
                pass
        return "break"

    def execute_command(self, event):
        """Execute a command in the terminal."""
        command = self.terminal_input.get().strip()
        if not command:
            return
            
        # Show the command being executed
        self.add_output(f"{self.prompt_label.cget('text')} {command}", "command")
        
        # Add to history
        if command not in self.command_history:
            self.command_history.insert(0, command)
            # Limit history size
            if len(self.command_history) > 100:
                self.command_history.pop()
        self.history_index = -1
        
        # Clear input
        self.terminal_input.delete(0, tk.END)
        
        # Handle built-in commands
        if self.handle_builtin_command(command):
            return
            
        # Execute external command
        self.start_animation("Executing...")
        threading.Thread(target=self.execute_external_command, args=(command,), daemon=True).start()

    def handle_builtin_command(self, command):
        """Handle built-in terminal commands."""
        parts = shlex.split(command) if command else []
        if not parts:
            return True
            
        cmd = parts[0].lower()
        
        if cmd == "clear":
            self.clear_terminal()
            return True
        elif cmd == "exit":
            self.parent.destroy()
            return True
        elif cmd == "status":
            self.show_system_status()
            return True
        elif cmd == "network":
            self.show_network_info()
            return True
            
        return False
    
    def show_system_status(self):
        """Show system status information."""
        try:
            import psutil
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            status_text = f"""🖥️  System Status:
   CPU Usage: {cpu_percent}% ({cpu_count} cores)
   Memory: {memory.percent}% ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)
   Disk: {disk.percent}% ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB used)
   Platform: {platform.system()} {platform.release()}
   Python: {sys.version.split()[0]}"""
            self.add_output(status_text, "info")
        except ImportError:
            self.add_output("System status requires 'psutil' package", "warning")
        except Exception as e:
            self.add_output(f"Error getting system status: {str(e)}", "error")

    def show_network_info(self):
        """Show network information."""
        try:
            hostname = socket.gethostname()
            try:
                local_ip = socket.gethostbyname(hostname)
            except:
                local_ip = "Unknown"
            
            network_text = f"""🌐 Network Information:
   Hostname: {hostname}
   Local IP: {local_ip}
   Platform: {platform.system()}"""
            self.add_output(network_text, "info")
        except Exception as e:
            self.add_output(f"Error getting network info: {str(e)}", "error")

    def execute_external_command(self, command):
        """Execute external system command."""
        try:
            # Change to current directory
            env = os.environ.copy()
            
            # Create process with proper settings for interactive input
            self.current_process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                cwd=self.current_directory,
                text=True,
                bufsize=0,  # Unbuffered
                universal_newlines=True,
                env=env
            )
            
            # Read output in real-time
            while True:
                # Check if process is still running
                if self.current_process.poll() is not None:
                    break
                
                # Try to read stdout
                try:
                    line = self.current_process.stdout.readline()
                    if line:
                        self.output_queue.put(('stdout', line.rstrip()))
                except:
                    pass
                
                # Small delay to prevent busy waiting
                time.sleep(0.01)
            
            # Get any remaining output
            try:
                remaining_stdout, remaining_stderr = self.current_process.communicate(timeout=1)
                if remaining_stdout:
                    self.output_queue.put(('stdout', remaining_stdout.rstrip()))
                if remaining_stderr:
                    self.output_queue.put(('stderr', remaining_stderr.rstrip()))
            except subprocess.TimeoutExpired:
                pass
            
            # Get return code
            return_code = self.current_process.poll()
            self.output_queue.put(('return_code', return_code))
            
        except Exception as e:
            self.output_queue.put(('error', f"Command error: {str(e)}"))
        finally:
            self.current_process = None
            self.output_queue.put(('done', None))

    def process_output(self):
        """Process command output from queue."""
        if self.is_destroyed:
            return
            
        try:
            while True:
                try:
                    msg_type, data = self.output_queue.get_nowait()
                    
                    if msg_type == 'stdout':
                        self.add_output(data, "output")
                    elif msg_type == 'stderr':
                        self.add_output(data, "error")
                    elif msg_type == 'return_code':
                        if data != 0:
                            self.add_output(f"Process exited with code: {data}", "warning")
                    elif msg_type == 'error':
                        self.add_output(data, "error")
                    elif msg_type == 'done':
                        self.stop_animation()
                        
                except queue.Empty:
                    break
        except Exception:
            pass
        
        # Schedule next check only if not destroyed
        if not self.is_destroyed:
            self.after(50, self.process_output)

    def start_animation(self, status_text):
        """Start loading animation."""
        if self.is_destroyed:
            return
            
        self.is_processing = True
        try:
            self.status_text.config(text=status_text, fg=self.colors["warning"])
            self.animate_status()
        except tk.TclError:
            self.is_destroyed = True

    def stop_animation(self):
        """Stop loading animation."""
        if self.is_destroyed:
            return
            
        self.is_processing = False
        try:
            self.status_text.config(text="Ready", fg=self.colors["success"])
            self.status_icon.config(text="●", fg=self.colors["success"])
        except tk.TclError:
            self.is_destroyed = True

    def animate_status(self):
        """Animate status icon."""
        if self.is_destroyed:
            return
            
        if self.is_processing:
            try:
                self.status_icon.config(text=self.animation_chars[self.animation_index], 
                                       fg=self.colors["warning"])
                self.animation_index = (self.animation_index + 1) % len(self.animation_chars)
                self.after(100, self.animate_status)
            except tk.TclError:
                self.is_destroyed = True

    def hide_terminal(self):
        """Hide the terminal panel - Fixed implementation."""
        try:
            # Find the main window by traversing up the widget hierarchy
            widget = self.parent
            while widget and not hasattr(widget, 'hide_terminal'):
                if hasattr(widget, 'master'):
                    widget = widget.master
                elif hasattr(widget, 'parent'):
                    widget = widget.parent
                else:
                    break
            
            # Call hide_terminal method if found
            if widget and hasattr(widget, 'hide_terminal'):
                widget.hide_terminal()
            else:
                # Alternative: try to find by checking for specific methods/attributes
                root_widget = self.winfo_toplevel()
                if hasattr(root_widget, 'hide_terminal'):
                    root_widget.hide_terminal()
                else:
                    # Last resort: destroy the widget
                    self.destroy()
                    
        except Exception as e:
            # If all else fails, mark as destroyed and hide
            self.is_destroyed = True
            try:
                self.pack_forget()
            except:
                pass

    def run_interactive_process(self, command, working_dir):
        """Run an interactive process that can handle user input."""
        try:
            self.add_output(f"Starting interactive process: {' '.join(command)}", "info")
            
            # Create interactive process
            self.current_process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=working_dir,
                text=True,
                bufsize=0
            )
            
            # Start reading output
            threading.Thread(target=self.read_interactive_output, daemon=True).start()
            
            # Enable input handling for interactive process
            self.terminal_input.bind("<Return>", self.send_input_to_process)
            
        except Exception as e:
            self.add_output(f"Error starting interactive process: {str(e)}", "error")

    def send_input_to_process(self, event):
        """Send user input to the running interactive process."""
        if self.current_process and self.current_process.poll() is None:
            user_input = self.terminal_input.get()
            self.add_output(f"> {user_input}", "input")
            
            try:
                self.current_process.stdin.write(user_input + "\n")
                self.current_process.stdin.flush()
                self.terminal_input.delete(0, tk.END)
            except Exception as e:
                self.add_output(f"Error sending input: {str(e)}", "error")
        else:
            # Process not running, restore normal command handling
            self.terminal_input.unbind("<Return>")
            self.terminal_input.bind("<Return>", self.execute_command)
            self.execute_command(event)
        
        return "break"

    def read_interactive_output(self):
        """Read output from interactive process."""
        try:
            while self.current_process and self.current_process.poll() is None:
                try:
                    # Read stdout
                    line = self.current_process.stdout.readline()
                    if line:
                        self.output_queue.put(('stdout', line.rstrip()))
                    
                    # Read stderr
                    if self.current_process.stderr.readable():
                        err_line = self.current_process.stderr.readline()
                        if err_line:
                            self.output_queue.put(('stderr', err_line.rstrip()))
                            
                except Exception:
                    break
                    
                time.sleep(0.01)
                
            # Process finished
            if self.current_process:
                return_code = self.current_process.poll()
                self.output_queue.put(('return_code', return_code))
                self.output_queue.put(('done', None))
                
                # Restore normal input handling
                try:
                    self.terminal_input.unbind("<Return>")
                    self.terminal_input.bind("<Return>", self.execute_command)
                except:
                    pass
                    
        except Exception as e:
            self.output_queue.put(('error', f"Interactive process error: {str(e)}"))

    def execute_code_from_editor(self, code, language):
        """Execute code from the editor in the terminal."""
        self.add_output(f"Executing {language} code...", "info")
        
        # Import the compiler here to avoid circular imports
        try:
            from editor.compiler import CodeCompiler
            compiler = CodeCompiler()
            
            # Run the code
            result = compiler.validate_and_execute(code, language)
            
            if result["syntax_valid"]:
                if result["success"]:
                    if result["stdout"]:
                        self.add_output("Output:", "success")
                        self.add_output(result["stdout"], "output")
                    else:
                        self.add_output("Code executed successfully (no output)", "success")
                else:
                    self.add_output("Execution failed:", "error")
                    if result["stderr"]:
                        self.add_output(result["stderr"], "error")
            else:
                self.add_output("Syntax Error:", "error")
                self.add_output(result["syntax_error"], "error")
                
        except ImportError:
            self.add_output("Compiler module not available", "error")
        except Exception as e:
            self.add_output(f"Error executing code: {str(e)}", "error")
            
    def destroy(self):
        """Override destroy to clean up properly."""
        self.is_destroyed = True
        
        # Terminate any running processes
        if self.current_process:
            try:
                self.current_process.terminate()
            except:
                pass
            
        # Call parent destroy
        super().destroy()