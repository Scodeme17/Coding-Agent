import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
import threading
from datetime import datetime
from agent.agent import CodingAgent
from editor.compiler import CodeCompiler
from gui.agent_gui import create_agent_panel, setup_enhanced_gui_methods
from gui.editor_gui import create_editor_panel
from gui.terminal_gui import AdvancedTerminal 


class ModernCodingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Coding Assistance Pro")
        self.root.geometry("1800x1200")
        self.root.configure(bg="#1e1e1e")
        
        # Modern color scheme
        self.colors = {
            "bg_primary": "#1e1e1e",      # Dark background
            "bg_secondary": "#252526",     # Slightly lighter
            "bg_tertiary": "#2d2d30",      # Panel backgrounds
            "accent": "#007acc",           # Blue accent
            "accent_hover": "#005a9e",     # Darker blue
            "text_primary": "#cccccc",     # Light text
            "text_secondary": "#969696",   # Dimmed text
            "success": "#4ec9b0",          # Teal for success
            "warning": "#dcdcaa",          # Yellow for warnings
            "error": "#f44747",            # Red for errors
            "border": "#3c3c3c"            # Border color
        }
        
        # Initialize components
        self.agent = None
        self.compiler = CodeCompiler()
        self.terminal_visible = False
        self.last_code_response = None
        self.loading = False
        
        # Initialize placeholder attributes
        self.is_placeholder = True
        self.query_count = 0
        self.success_count = 0
        self.code_block_count = 0
        
        # Setup enhanced GUI methods first
        setup_enhanced_gui_methods(self)
        
        # Initialize agent in separate thread to avoid blocking UI
        self.initialize_agent_async()
        
        # Setup custom styles
        self.setup_styles()
        
        # Build the interface
        self.build_interface()
        
        # Configure text widgets colors
        self.configure_text_widgets()

    def initialize_agent_async(self):
        """Initialize agent in a separate thread to avoid blocking UI."""
        def init_agent():
            try:
                self.agent = CodingAgent()
                self.root.after(0, lambda: self.update_agent_status(True))
                self.root.after(0, lambda: self.add_chat_message("System", "AI Assistant ready! 🚀", "assistant"))
            except Exception as e:
                error_msg = f"Failed to initialize AI agent: {str(e)}\nPlease check your GROQ_API_KEY in .env file"
                self.root.after(0, lambda: self.update_agent_status(False))
                self.root.after(0, lambda: self.add_chat_message("System", error_msg, "error"))
        
        thread = threading.Thread(target=init_agent, daemon=True)
        thread.start()

    def setup_styles(self):
        """Configure custom ttk styles for modern appearance."""
        style = ttk.Style()
        
        # Configure frame styles
        style.configure("Primary.TFrame", background=self.colors["bg_primary"])
        style.configure("Secondary.TFrame", background=self.colors["bg_secondary"])
        style.configure("Tertiary.TFrame", background=self.colors["bg_tertiary"])
        
        # Configure button styles
        style.configure("Accent.TButton",
                       background=self.colors["accent"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none")
        style.map("Accent.TButton",
                 background=[("active", self.colors["accent_hover"])])
        
        # Configure success button styles
        style.configure("Success.TButton",
                       background=self.colors["success"],
                       foreground="white",
                       borderwidth=0,
                       focuscolor="none")
        style.map("Success.TButton",
                 background=[("active", "#3fa894")])
        
        # Configure warning button styles
        style.configure("Warning.TButton",
                       background=self.colors["warning"],
                       foreground="black",
                       borderwidth=0,
                       focuscolor="none")
        style.map("Warning.TButton",
                 background=[("active", "#b8b86b")])
        
        # Configure terminal button styles
        style.configure("Terminal.TButton",
                       background=self.colors["bg_tertiary"],
                       foreground=self.colors["text_primary"],
                       borderwidth=1,
                       focuscolor="none")
        style.map("Terminal.TButton",
                 background=[("active", self.colors["bg_secondary"])])
                 
        # Configure quick button styles
        style.configure("Quick.TButton",
                       background=self.colors["bg_secondary"],
                       foreground=self.colors["text_primary"],
                       borderwidth=1,
                       focuscolor="none")
        style.map("Quick.TButton",
                 background=[("active", self.colors["bg_tertiary"])])
        
        # Configure entry styles
        style.configure("Modern.TEntry",
                       fieldbackground=self.colors["bg_tertiary"],
                       foreground=self.colors["text_primary"],
                       borderwidth=1,
                       insertcolor=self.colors["text_primary"])
        
        # Configure labelframe styles
        style.configure("Modern.TLabelframe",
                       background=self.colors["bg_tertiary"],
                       foreground=self.colors["text_primary"],
                       borderwidth=1)
        style.configure("Modern.TLabelframe.Label",
                       background=self.colors["bg_tertiary"],
                       foreground=self.colors["text_primary"])
                       
        # Configure radiobutton styles
        style.configure("Modern.TRadiobutton",
                       background=self.colors["bg_tertiary"],
                       foreground=self.colors["text_primary"],
                       focuscolor="none")
        
        # Configure combobox styles
        style.configure("Modern.TCombobox",
                       fieldbackground="#000000",
                       foreground="white",
                       background="#000000",
                       borderwidth=1,
                       relief="solid")
        style.map("Modern.TCombobox",
                 fieldbackground=[("readonly", "#000000")],
                 foreground=[("readonly", "white")],
                 background=[("readonly", "#000000")])

    def build_interface(self):
        """Build the main interface layout."""
        # Main container
        main_container = ttk.Frame(self.root, style="Primary.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main content area with horizontal paned window for 50-50 split
        self.main_paned = ttk.PanedWindow(main_container, orient='horizontal')
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Code Editor with terminal (50% width)
        create_editor_panel(self, self.main_paned)
        
        # Right panel - Agent Chat (50% width)
        create_agent_panel(self, self.main_paned)
        
        # Set 50-50 split after the window is mapped
        self.root.after(100, self.set_equal_split)

    def set_equal_split(self):
        """Set the paned window to 50-50 split."""
        total_width = self.main_paned.winfo_width()
        if total_width > 1:
            self.main_paned.sashpos(0, total_width // 2)

    def configure_text_widgets(self):
        """Configure colors for text widgets."""
        # Chat display colors
        self.chat_display.configure(
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            selectbackground=self.colors["accent"],
            selectforeground="white"
        )
        
        # Code editor colors
        self.code_editor.configure(
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["accent"],
            selectbackground=self.colors["accent"],
            selectforeground="white"
        )

    def update_line_numbers(self, event=None):
        """Update line numbers in the code editor."""
        try:
            line_count = int(self.code_editor.index('end-1c').split('.')[0])
            line_numbers = '\n'.join(str(i) for i in range(1, line_count + 1))
            
            self.line_numbers.config(state='normal')
            self.line_numbers.delete('1.0', tk.END)
            self.line_numbers.insert('1.0', line_numbers)
            self.line_numbers.config(state='disabled')
        except Exception:
            pass  # Ignore errors during line number updates

    def sync_scroll(self, event):
        """Synchronize scrolling between line numbers and code editor."""
        try:
            self.line_numbers.yview_moveto(self.code_editor.yview()[0])
        except Exception:
            pass

    def on_language_change(self, event=None):
        """Handle language selection change."""
        language = self.language_var.get()
        if hasattr(self, 'terminal') and self.terminal_visible:
            self.terminal.add_output(f"Language switched to {language.upper()}", "info")

    def on_typing(self, event):
        """Handle typing in query input."""
        # Enable send button when there's text
        if hasattr(self, 'send_button'):
            text = self.query_input.get().strip()
            if text and not self.loading:
                self.send_button.configure(state='normal')
            else:
                self.send_button.configure(state='disabled')

    # Terminal methods
    def toggle_terminal(self):
        """Toggle the terminal panel visibility (VS Code style)."""
        if self.terminal_visible:
            self.hide_terminal()
        else:
            self.show_terminal()

    def show_terminal(self):
        """Show the terminal panel."""
        if not self.terminal_visible and hasattr(self, 'paned_window'):
            self.paned_window.add(self.terminal_frame, weight=1)
            self.terminal_visible = True
            # Update button appearance
            if hasattr(self, 'terminal_button'):
                self.terminal_button.configure(text="🐧↓")
            # Set initial position (70% editor, 30% terminal)
            self.root.after(1, lambda: self.paned_window.sashpos(0, int(self.paned_window.winfo_height() * 0.6)))
            # Focus on terminal input
            if hasattr(self, 'terminal'):
                self.terminal.terminal_input.focus_set()

    def hide_terminal(self):
        """Hide the terminal panel."""
        if self.terminal_visible and hasattr(self, 'paned_window'):
            self.paned_window.forget(self.terminal_frame)
            self.terminal_visible = False
            # Update button appearance
            if hasattr(self, 'terminal_button'):
                self.terminal_button.configure(text="🐧")

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

    def process_query(self):
        """Process user query through the AI agent."""
        if self.loading or not self.agent:
            if not self.agent:
                self.add_chat_message("System", "AI agent is still initializing. Please wait...", "system")
            return
            
        query = self.query_input.get().strip()
        if not query or query == self.placeholder_text:
            return
        
        # Set loading state
        self.loading = True
        self.query_input.delete(0, tk.END)
        self.query_input.configure(state='disabled')
        if hasattr(self, 'send_button'):
            self.send_button.configure(state='disabled', text="Processing...")
        
        self.add_chat_message("You", query, "user")
        
        # Update query count
        self.query_count += 1
        
        # Process query in separate thread to avoid blocking UI
        def process_in_thread():
            try:
                result = self.agent.process_query(query)
                
                # Update UI in main thread
                self.root.after(0, lambda: self.handle_query_result(result))
                
            except Exception as e:
                error_msg = f"Error processing query: {str(e)}"
                self.root.after(0, lambda: self.add_chat_message("AI", error_msg, "error"))
            finally:
                # Reset loading state in main thread
                self.root.after(0, self.reset_loading_state)
        
        thread = threading.Thread(target=process_in_thread, daemon=True)
        thread.start()

    def handle_query_result(self, result):
        """Handle the result from query processing."""
        if result['success']:
            self.add_chat_message("AI", result['content'], "assistant")
            self.success_count += 1
            
            if result['code_blocks']:
                self.last_code_response = result['code_blocks']
                self.code_block_count += len(result['code_blocks'])
                
                # Auto-load first code block to editor
                code_block = result['code_blocks'][0]
                self.code_editor.delete("1.0", tk.END)
                self.code_editor.insert("1.0", code_block['code'])
                
                # Set appropriate language
                lang_map = {
                    "python": "🐍", "java": "☕", "javascript": "js", 
                    "c": "c", "cpp": "cpp", "go": "go"
                }
                self.language_var.set(lang_map.get(code_block['language'], "🐍"))
                
                self.update_line_numbers()
                
                # Show success message
                if hasattr(self, 'terminal'):
                    self.show_terminal()
                    self.terminal.add_output("✅ Code loaded to editor automatically!", "success")
        else:
            self.add_chat_message("AI", result['content'], "error")
        
        # Update statistics
        self.update_statistics()

    def reset_loading_state(self):
        """Reset the loading state of UI components."""
        self.loading = False
        self.query_input.configure(state='normal')
        if hasattr(self, 'send_button'):
            self.send_button.configure(state='normal', text="🚀 Send Query")
        # Set placeholder text if empty
        if not self.query_input.get():
            self.set_placeholder_text()

    def run_code(self):
        """Execute the code in the editor."""
        code = self.code_editor.get("1.0", tk.END).strip()
        if not code:
            self.show_terminal()
            if hasattr(self, 'terminal'):
                self.terminal.add_output("❌ No code to execute.", "error")
            return
        
        language = self.language_var.get()
        lang_map = {"🐍": "python", "☕": "java", "js": "javascript", "c": "c", "cpp": "cpp", "go": "go"}
        actual_lang = lang_map.get(language, "python")
        
        self.show_terminal()
        if hasattr(self, 'terminal'):
            self.terminal.add_output(f"🚀 Executing {actual_lang.upper()} code...", "info")
            self.terminal.add_output("=" * 50, "info")
        
        try:
            result = self.compiler.run_code(code, actual_lang)
            
            if hasattr(self, 'terminal'):
                if result['success']:
                    if result['stdout']:
                        self.terminal.add_output(f"✅ Output:\n{result['stdout']}", "success")
                    else:
                        self.terminal.add_output("✅ Code executed successfully (no output)", "success")
                else:
                    if result.get('error'):
                        self.terminal.add_output(f"❌ Execution Error:\n{result['error']}", "error")
                    if result['stderr']:
                        self.terminal.add_output(f"❌ Standard Error:\n{result['stderr']}", "error")
                    if result.get('return_code') is not None:
                        self.terminal.add_output(f"Return code: {result['return_code']}", "warning")
                
        except Exception as e:
            error_msg = f"❌ Execution error: {str(e)}"
            if hasattr(self, 'terminal'):
                self.terminal.add_output(error_msg, "error")

    def load_to_editor(self):
        """Load the last AI code response to the code editor."""
        if not self.last_code_response:
            self.add_chat_message("System", "No code solution available to load.", "system")
            return
        
        try:
            code_block = self.last_code_response[0]
            
            self.code_editor.delete("1.0", tk.END)
            self.code_editor.insert("1.0", code_block['code'])
            
            # Set appropriate language
            lang_map = {
                "python": "🐍", "java": "☕", "javascript": "js", 
                "c": "c", "cpp": "cpp", "go": "go"
            }
            self.language_var.set(lang_map.get(code_block['language'], "🐍"))
            
            self.update_line_numbers()
            
            self.add_chat_message("System", "Code solution loaded to editor", "system")
            
            if hasattr(self, 'terminal'):
                self.show_terminal()
                self.terminal.add_output("✅ Code solution loaded to editor successfully!", "success")
            
        except Exception as e:
            error_msg = f"❌ Error loading code: {str(e)}"
            self.add_chat_message("System", error_msg, "error")

    

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernCodingGUI(root)
    root.mainloop()