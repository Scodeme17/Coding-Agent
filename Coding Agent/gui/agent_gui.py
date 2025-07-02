import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
from datetime import datetime
import threading
import re

def create_agent_panel(self, parent):
    """Create the enhanced AI agent chat panel with advanced features."""
    # Agent panel container
    agent_container = ttk.Frame(parent, style="Tertiary.TFrame")
    
    # Enhanced agent panel header with more controls
    agent_header = ttk.Frame(agent_container, style="Secondary.TFrame")
    agent_header.pack(fill=tk.X, padx=5, pady=5)
    
    # Title and status indicator
    title_frame = ttk.Frame(agent_header, style="Secondary.TFrame")
    title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=5)
    
    # Agent status indicator
    self.agent_status_label = tk.Label(title_frame, text="🤖 AI Coding Assistant", 
                                      bg=self.colors["bg_secondary"], 
                                      fg=self.colors["text_primary"],
                                      font=("Segoe UI", 12, "bold"))
    self.agent_status_label.pack(side=tk.LEFT)
    
    # Status indicator (online/offline)
    self.status_indicator = tk.Label(title_frame, text="⚫", 
                                   bg=self.colors["bg_secondary"],
                                   fg=self.colors["error"],
                                   font=("Segoe UI", 14))
    self.status_indicator.pack(side=tk.LEFT, padx=(10, 0))
    
    # Control buttons frame
    control_frame = ttk.Frame(agent_header, style="Secondary.TFrame")
    control_frame.pack(side=tk.RIGHT, padx=10, pady=4)
    
    # Enhanced control buttons
    self.load_button = ttk.Button(control_frame, text="📥", 
                                style="Accent.TButton", command=self.load_to_editor)
    self.load_button.pack(side=tk.LEFT, padx=2)
    
    self.clear_button = ttk.Button(control_frame, text="🧹", 
                                 style="Warning.TButton", command=self.clear_chat)
    self.clear_button.pack(side=tk.LEFT, padx=2)
    
    
    # Agent configuration frame
    config_frame = ttk.Frame(agent_container, style="Tertiary.TFrame")
    config_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
    
    # Left side - Query mode selection
    mode_frame = ttk.LabelFrame(config_frame, text="Query Mode", style="Modern.TLabelframe")
    mode_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    self.query_mode = tk.StringVar(value="auto")
    modes = [
        ("🧠 Auto Detect", "auto"),
        ("💻 Code Generation", "generation"),
        ("🔧 Debug & Fix", "debug"),
        ("📚 Explanation", "explanation"),
        ("🚀 Optimization", "optimization"),
        ("🧪 Testing", "testing")
    ]
    
    for text, value in modes:
        ttk.Radiobutton(mode_frame, text=text, variable=self.query_mode, 
                       value=value, style="Modern.TRadiobutton").pack(anchor=tk.W, padx=5, pady=1)
    
    # Right side - Complexity level
    complexity_frame = ttk.LabelFrame(config_frame, text="Complexity Level", style="Modern.TLabelframe")
    complexity_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
    
    self.complexity_level = tk.StringVar(value="adaptive")
    complexities = [
        ("🌟 Adaptive", "adaptive"),
        ("🟢 Beginner", "beginner"),
        ("🟡 Intermediate", "intermediate"),
        ("🔴 Advanced", "advanced"),
        ("🏆 Expert", "expert")
    ]
    
    for text, value in complexities:
        ttk.Radiobutton(complexity_frame, text=text, variable=self.complexity_level, 
                       value=value, style="Modern.TRadiobutton").pack(anchor=tk.W, padx=5, pady=1)
    
    # Enhanced chat display area with syntax highlighting
    chat_frame = ttk.Frame(agent_container, style="Tertiary.TFrame")
    chat_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
    
    # Chat display with custom tags for better formatting
    self.chat_display = scrolledtext.ScrolledText(
        chat_frame,
        wrap=tk.WORD,
        font=("Consolas", 10),
        height=20,
        state='disabled',
        cursor="arrow"
    )
    self.chat_display.pack(fill=tk.BOTH, expand=True)
    
    # Configure text tags for better message formatting
    self.setup_chat_tags()
    
    # Statistics panel
    stats_frame = ttk.Frame(agent_container, style="Secondary.TFrame")
    stats_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
    
    self.stats_label = tk.Label(stats_frame, 
                               text="📊 Queries: 0 | Code Blocks: 0 | Success Rate: 0%",
                               bg=self.colors["bg_secondary"], 
                               fg=self.colors["text_secondary"],
                               font=("Segoe UI", 9))
    self.stats_label.pack(side=tk.LEFT, padx=10, pady=5)
    
    # Enhanced query input area with smart features
    input_container = ttk.Frame(agent_container, style="Tertiary.TFrame")
    input_container.pack(fill=tk.X, padx=5, pady=(0, 5))
    
    # Quick action buttons for common queries
    quick_actions_frame = ttk.Frame(input_container, style="Tertiary.TFrame")
    quick_actions_frame.pack(fill=tk.X, pady=(0, 5))
    
    tk.Label(quick_actions_frame, text="Quick Actions:", 
            bg=self.colors["bg_tertiary"], 
            fg=self.colors["text_secondary"],
            font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
    
    quick_buttons = [
        ("🔍 Debug Code", "Debug and fix issues in my code"),
        ("⚡ Optimize", "Optimize my code for better performance"),
        ("📖 Explain", "Explain how this code works"),
        ("🧪 Test", "Generate test cases for my code")
    ]
    
    for text, query in quick_buttons:
        btn = ttk.Button(quick_actions_frame, text=text, 
                        style="Quick.TButton",
                        command=lambda q=query: self.set_quick_query(q))
        btn.pack(side=tk.LEFT, padx=2)
    
    # Enhanced input field with autocomplete suggestions
    input_frame = ttk.Frame(input_container, style="Tertiary.TFrame")
    input_frame.pack(fill=tk.X, pady=(5, 0))
    
    # Input field with placeholder text
    self.query_input = ttk.Entry(input_frame, style="Modern.TEntry", font=("Segoe UI", 11))
    self.query_input.pack(fill=tk.X, pady=(0, 8))
    self.query_input.bind('<Return>', lambda e: self.process_query())
    self.query_input.bind('<KeyPress>', self.on_typing)
    self.query_input.bind('<KeyRelease>', self.on_input_change)
    self.query_input.bind('<FocusIn>', self.on_input_focus)
    self.query_input.bind('<FocusOut>', self.on_input_unfocus)
    
    # Set placeholder text
    self.set_placeholder_text()
    
    # Enhanced send button with loading state
    button_frame = ttk.Frame(input_frame, style="Tertiary.TFrame")
    button_frame.pack(fill=tk.X)
    
    self.send_button = ttk.Button(button_frame, text="🚀 Send Query", 
                                style="Accent.TButton", command=self.process_query)
    self.send_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    
    # Initialize statistics
    self.query_count = 0
    self.success_count = 0
    self.code_block_count = 0
    
    # Add to paned window
    parent.add(agent_container, weight=1)

def setup_chat_tags(self):
    """Setup enhanced text formatting tags for chat display."""
    # User message tags
    self.chat_display.tag_configure("user_prefix", 
                                   foreground=self.colors["accent"], 
                                   font=("Segoe UI", 10, "bold"))
    self.chat_display.tag_configure("user_message", 
                                   foreground=self.colors["text_primary"],
                                   font=("Segoe UI", 10))
    
    # AI message tags
    self.chat_display.tag_configure("ai_prefix", 
                                   foreground=self.colors["success"], 
                                   font=("Segoe UI", 10, "bold"))
    self.chat_display.tag_configure("ai_message", 
                                   foreground=self.colors["text_primary"],
                                   font=("Segoe UI", 10))
    
    # System message tags
    self.chat_display.tag_configure("system_prefix", 
                                   foreground=self.colors["warning"], 
                                   font=("Segoe UI", 10, "bold"))
    self.chat_display.tag_configure("system_message", 
                                   foreground=self.colors["text_secondary"],
                                   font=("Segoe UI", 10, "italic"))
    
    # Error message tags
    self.chat_display.tag_configure("error_prefix", 
                                   foreground=self.colors["error"], 
                                   font=("Segoe UI", 10, "bold"))
    self.chat_display.tag_configure("error_message", 
                                   foreground=self.colors["error"],
                                   font=("Segoe UI", 10))
    
    # Code block tags
    self.chat_display.tag_configure("code_block", 
                                   background="#2d2d30",
                                   foreground="#dcdcaa",
                                   font=("Consolas", 10),
                                   relief="solid",
                                   borderwidth=1)
    
    # Inline code tags
    self.chat_display.tag_configure("inline_code", 
                                   background="#2d2d30",
                                   foreground="#4ec9b0",
                                   font=("Consolas", 10))

def set_placeholder_text(self):
    """Set placeholder text for the input field."""
    self.placeholder_text = "Ask me anything about coding, debugging, algorithms, ML, data analysis..."
    self.query_input.insert(0, self.placeholder_text)
    self.query_input.configure(foreground=self.colors["text_secondary"])
    self.is_placeholder = True

def on_input_focus(self, event):
    """Handle input field focus."""
    if self.is_placeholder:
        self.query_input.delete(0, tk.END)
        self.query_input.configure(foreground=self.colors["text_primary"])
        self.is_placeholder = False

def on_input_unfocus(self, event):
    """Handle input field unfocus."""
    if not self.query_input.get().strip():
        self.set_placeholder_text()

def on_input_change(self, event):
    """Handle input field changes for smart suggestions."""
    if self.is_placeholder:
        return
    
    text = self.query_input.get().lower()
    
    # Simple autocomplete suggestions (can be enhanced with AI)
    suggestions = {
        "python": ["python list comprehension", "python decorators", "python async/await"],
        "java": ["java collections", "java streams", "java multithreading"],
        "debug": ["debug python code", "debug javascript", "debug memory leaks"],
        "algorithm": ["sorting algorithms", "graph algorithms", "dynamic programming"],
        "ml": ["machine learning python", "tensorflow tutorial", "data preprocessing"],
        "sql": ["sql joins", "sql optimization", "database design"]
    }
    
    # This is a placeholder for more advanced autocomplete functionality

def set_quick_query(self, query):
    """Set a quick query in the input field."""
    if self.is_placeholder:
        self.query_input.delete(0, tk.END)
        self.query_input.configure(foreground=self.colors["text_primary"])
        self.is_placeholder = False
    else:
        self.query_input.delete(0, tk.END)
    
    self.query_input.insert(0, query)

def voice_input_placeholder(self):
    """Placeholder for voice input functionality."""
    messagebox.showinfo("Voice Input", "Voice input feature coming soon!\nCurrently in development.")

def clear_chat(self):
    """Clear the chat history with confirmation."""
    if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat history?"):
        self.chat_display.config(state='normal')
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state='disabled')
        
        # Reset statistics
        self.query_count = 0
        self.success_count = 0
        self.code_block_count = 0
        self.update_statistics()
        
        # Clear agent history if available
        if hasattr(self, 'agent') and self.agent:
            self.agent.clear_chat_history()
        
        self.add_chat_message("System", "Chat history cleared successfully!", "system")

def save_chat_history(self):
    """Enhanced save chat history with metadata."""
    if not hasattr(self, 'agent') or not self.agent:
        messagebox.showerror("Error", "AI agent not initialized!")
        return
    
    filename = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Save Chat History"
    )
    
    if filename:
        try:
            # Get chat history from agent
            history = self.agent.get_chat_history()
            
            # Add metadata
            save_data = {
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "total_queries": self.query_count,
                    "success_count": self.success_count,
                    "code_blocks": self.code_block_count,
                    "success_rate": (self.success_count / max(self.query_count, 1)) * 100
                },
                "chat_history": history
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Chat history saved to {filename}")
            self.add_chat_message("System", f"Chat history saved to {os.path.basename(filename)}", "system")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save chat history: {str(e)}")

def load_chat_history(self):
    """Enhanced load chat history with validation."""
    filename = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        title="Load Chat History"
    )
    
    if filename:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle both old and new format
            if isinstance(data, dict) and "chat_history" in data:
                history = data["chat_history"]
                metadata = data.get("metadata", {})
            else:
                history = data
                metadata = {}
            
            # Clear current chat
            self.chat_display.config(state='normal')
            self.chat_display.delete('1.0', tk.END)
            self.chat_display.config(state='disabled')
            
            # Load history into agent
            if hasattr(self, 'agent') and self.agent:
                self.agent.chat_history = history
            
            # Display loaded messages
            for entry in history:
                self.add_chat_message("You", entry['query'], "user")
                self.add_chat_message("AI", entry['response'], "assistant")
            
            # Update statistics from metadata
            if metadata:
                self.query_count = metadata.get("total_queries", 0)
                self.success_count = metadata.get("success_count", 0)
                self.code_block_count = metadata.get("code_blocks", 0)
                self.update_statistics()
            
            messagebox.showinfo("Success", f"Chat history loaded from {filename}")
            self.add_chat_message("System", f"Chat history loaded from {os.path.basename(filename)}", "system")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load chat history: {str(e)}")

def update_statistics(self):
    """Update the statistics display."""
    success_rate = (self.success_count / max(self.query_count, 1)) * 100
    stats_text = f"📊 Queries: {self.query_count} | Code Blocks: {self.code_block_count} | Success Rate: {success_rate:.1f}%"
    self.stats_label.configure(text=stats_text)

def update_agent_status(self, online=True):
    """Update the agent status indicator."""
    if online:
        self.status_indicator.configure(text="🟢", fg=self.colors["success"])
        self.agent_status_label.configure(text="🤖 AI Coding Assistant (Online)")
    else:
        self.status_indicator.configure(text="🔴", fg=self.colors["error"])
        self.agent_status_label.configure(text="🤖 AI Coding Assistant (Offline)")

# Enhanced message formatting with code highlighting
def add_chat_message_enhanced(self, sender, message, msg_type="info"):
    """Enhanced message display with code syntax highlighting."""
    self.chat_display.config(state='normal')
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Message formatting based on type
    if msg_type == "user":
        prefix = f"[{timestamp}] 👤 {sender}: "
        prefix_tag = "user_prefix"
        message_tag = "user_message"
    elif msg_type == "assistant":
        prefix = f"[{timestamp}] 🤖 {sender}: "
        prefix_tag = "ai_prefix"
        message_tag = "ai_message"
    elif msg_type == "error":
        prefix = f"[{timestamp}] ❌ {sender}: "
        prefix_tag = "error_prefix"
        message_tag = "error_message"
    elif msg_type == "system":
        prefix = f"[{timestamp}] ⚙️ {sender}: "
        prefix_tag = "system_prefix"
        message_tag = "system_message"
    else:
        prefix = f"[{timestamp}] {sender}: "
        prefix_tag = "system_prefix"
        message_tag = "system_message"
    
    # Insert prefix
    self.chat_display.insert(tk.END, prefix, prefix_tag)
    
    # Parse and insert message with code highlighting
    self.insert_message_with_formatting(message, message_tag)
    
    self.chat_display.insert(tk.END, "\n\n")
    self.chat_display.see(tk.END)
    self.chat_display.config(state='disabled')

def insert_message_with_formatting(self, message, default_tag):
    """Insert message with code block and inline code formatting."""
    # Find code blocks
    code_block_pattern = r'```(\w+)?\n?(.*?)```'
    inline_code_pattern = r'`([^`\n]+)`'
    
    last_end = 0
    
    # Process code blocks first
    for match in re.finditer(code_block_pattern, message, re.DOTALL):
        # Insert text before code block
        if match.start() > last_end:
            text_before = message[last_end:match.start()]
            self.insert_text_with_inline_code(text_before, default_tag)
        
        # Insert code block
        lang = match.group(1) or "text"
        code = match.group(2).strip()
        
        self.chat_display.insert(tk.END, f"\n[{lang.upper()} CODE]\n", "system_prefix")
        self.chat_display.insert(tk.END, code, "code_block")
        self.chat_display.insert(tk.END, "\n[END CODE]\n", "system_prefix")
        
        last_end = match.end()
    
    # Insert remaining text
    if last_end < len(message):
        remaining_text = message[last_end:]
        self.insert_text_with_inline_code(remaining_text, default_tag)

def insert_text_with_inline_code(self, text, default_tag):
    """Insert text with inline code formatting."""
    inline_code_pattern = r'`([^`\n]+)`'
    last_end = 0
    
    for match in re.finditer(inline_code_pattern, text):
        # Insert normal text
        if match.start() > last_end:
            self.chat_display.insert(tk.END, text[last_end:match.start()], default_tag)
        
        # Insert inline code
        self.chat_display.insert(tk.END, match.group(1), "inline_code")
        last_end = match.end()
    
    # Insert remaining text
    if last_end < len(text):
        self.chat_display.insert(tk.END, text[last_end:], default_tag)

# Replace the original add_chat_message method with the enhanced version
def setup_enhanced_gui_methods(self):
    """Setup enhanced GUI methods."""
    # Replace methods with enhanced versions
    self.add_chat_message = lambda sender, message, msg_type="info": add_chat_message_enhanced(self, sender, message, msg_type)
    self.setup_chat_tags = lambda: setup_chat_tags(self)
    self.set_placeholder_text = lambda: set_placeholder_text(self)
    self.on_input_focus = lambda event: on_input_focus(self, event)
    self.on_input_unfocus = lambda event: on_input_unfocus(self, event)
    self.on_input_change = lambda event: on_input_change(self, event)
    self.set_quick_query = lambda query: set_quick_query(self, query)
    self.voice_input_placeholder = lambda: voice_input_placeholder(self)
    self.clear_chat = lambda: clear_chat(self)
    self.save_chat_history = lambda: save_chat_history(self)
    self.load_chat_history = lambda: load_chat_history(self)
    self.update_statistics = lambda: update_statistics(self)
    self.update_agent_status = lambda online=True: update_agent_status(self, online)
    self.insert_message_with_formatting = lambda message, tag: insert_message_with_formatting(self, message, tag)
    self.insert_text_with_inline_code = lambda text, tag: insert_text_with_inline_code(self, text, tag)