import os
import re
import subprocess
import tempfile
import shutil
import py_compile
import threading
import signal
from datetime import datetime
from typing import Optional, Tuple, Dict, Any, List
from pathlib import Path


class CodeCompiler:
    """Enhanced code compiler supporting Python, Go, Java, C, and C++ with improved error handling and security."""
    
    def __init__(self):
        self.supported_languages = ["python", "go", "java", "c", "cpp"]
        
        # Compiler configurations with proper command structures
        self.compilers = {
            "python": {
                "command": ["python3", "{file}"],
                "fallback": ["python", "{file}"],
                "compile": None,
                "extension": ".py"
            },
            "go": {
                "command": ["go", "run", "{file}"],
                "compile": ["go", "build", "-o", "{output}", "{file}"],
                "extension": ".go"
            },
            "java": {
                "command": ["java", "{class}"],
                "compile": ["javac", "{file}"],
                "extension": ".java"
            },
            "c": {
                "command": ["{output}"],
                "compile": ["gcc", "-o", "{output}", "{file}", "-lm"],
                "extension": ".c"
            },
            "cpp": {
                "command": ["{output}"],
                "compile": ["g++", "-o", "{output}", "{file}", "-lm"],
                "extension": ".cpp" or ".c++"
            }
        }
        
        # Security settings
        self.max_execution_time = 30  # seconds
        self.max_output_size = 1024 * 1024  # 1MB
        
        # Check available compilers
        self._check_compiler_availability()

    def _check_compiler_availability(self):
        """Check which compilers are available on the system."""
        self.available_compilers = {}
        
        # Check Python
        if shutil.which("python3"):
            self.available_compilers["python"] = "python3"
        elif shutil.which("python"):
            self.available_compilers["python"] = "python"
        
        # Check other compilers
        compiler_checks = {
            "go": "go",
            "java": "javac",
            "c": "gcc",
            "cpp": "g++"
        }
        
        for lang, compiler in compiler_checks.items():
            if shutil.which(compiler):
                self.available_compilers[lang] = compiler

    def is_language_supported(self, language: str) -> bool:
        """Check if the programming language is supported and available."""
        return language.lower() in self.available_compilers

    def get_available_languages(self) -> List[str]:
        """Get list of available programming languages."""
        return list(self.available_compilers.keys())

    def get_file_extension(self, language: str) -> str:
        """Get the file extension for a given programming language."""
        return self.compilers.get(language.lower(), {}).get("extension", ".txt")

    def extract_code_blocks(self, text: str) -> List[Tuple[str, str]]:
        """Extract code blocks from markdown text."""
        # Match both ``` and ~~~ code blocks
        patterns = [
            r'```(\w+)?\n?(.*?)```',
            r'~~~(\w+)?\n?(.*?)~~~'
        ]
        
        code_blocks = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for lang, code in matches:
                language = lang.lower() if lang else "python"
                code_blocks.append((language, code.strip()))
        
        return code_blocks

    def _create_secure_temp_dir(self) -> str:
        """Create a secure temporary directory for code execution."""
        temp_dir = tempfile.mkdtemp(prefix="code_exec_")
        os.chmod(temp_dir, 0o700)  # Restrict access to owner only
        return temp_dir

    def check_syntax(self, code: str, language: str) -> Optional[str]:
        """Check syntax for the given code and language."""
        language = language.lower()
        
        if not self.is_language_supported(language):
            return f"Language '{language}' is not supported or compiler not available"
        
        try:
            if language == "python":
                return self._check_python_syntax(code)
            elif language == "go":
                return self._check_go_syntax(code)
            elif language == "java":
                return self._check_java_syntax(code)
            elif language in ["c", "cpp"]:
                return self._check_c_cpp_syntax(code, language)
            else:
                return f"Syntax checking for {language} is not implemented"
        except Exception as e:
            return f"Syntax check error: {str(e)}"

    def _check_python_syntax(self, code: str) -> Optional[str]:
        """Check Python syntax using AST compilation."""
        try:
            # First try AST compilation (faster)
            compile(code, '<string>', 'exec')
            return None
        except SyntaxError as e:
            return f"Syntax Error at line {e.lineno}: {e.msg}"
        except Exception as e:
            return f"Python syntax error: {str(e)}"

    def _check_go_syntax(self, code: str) -> Optional[str]:
        """Check Go syntax."""
        temp_dir = self._create_secure_temp_dir()
        try:
            temp_file = os.path.join(temp_dir, "main.go")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            result = subprocess.run(
                ["go", "build", "-o", "/dev/null", temp_file],
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                cwd=temp_dir
            )
            
            if result.returncode != 0:
                # Clean up Go-specific error messages
                error = result.stderr.replace(temp_file + ":", "")
                return error.strip()
            return None
            
        except subprocess.TimeoutExpired:
            return "Syntax check timed out"
        except Exception as e:
            return f"Go syntax check error: {str(e)}"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _check_java_syntax(self, code: str) -> Optional[str]:
        """Check Java syntax."""
        temp_dir = self._create_secure_temp_dir()
        try:
            # Extract class name from code
            class_match = re.search(r'public\s+class\s+(\w+)', code)
            class_name = class_match.group(1) if class_match else "Main"
            
            temp_file = os.path.join(temp_dir, f"{class_name}.java")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            result = subprocess.run(
                ["javac", temp_file],
                stderr=subprocess.PIPE,
                text=True,
                timeout=15,
                cwd=temp_dir
            )
            
            if result.returncode != 0:
                # Clean up Java-specific error messages
                error = result.stderr.replace(temp_file + ":", "")
                return error.strip()
            return None
            
        except subprocess.TimeoutExpired:
            return "Syntax check timed out"
        except Exception as e:
            return f"Java syntax check error: {str(e)}"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _check_c_cpp_syntax(self, code: str, language: str) -> Optional[str]:
        """Check C/C++ syntax."""
        temp_dir = self._create_secure_temp_dir()
        try:
            compiler = "gcc" if language == "c" else "g++"
            extension = ".c" if language == "c" else ".cpp"
            temp_file = os.path.join(temp_dir, f"main{extension}")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            result = subprocess.run(
                [compiler, "-fsyntax-only", "-Wall", temp_file],
                stderr=subprocess.PIPE,
                text=True,
                timeout=10,
                cwd=temp_dir
            )
            
            if result.returncode != 0:
                # Clean up compiler-specific error messages
                error = result.stderr.replace(temp_file + ":", "")
                return error.strip()
            return None
            
        except subprocess.TimeoutExpired:
            return "Syntax check timed out"
        except Exception as e:
            return f"{language.upper()} syntax check error: {str(e)}"
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def run_code(self, code: str, language: str, timeout: int = None) -> Dict[str, Any]:
        """Execute code in the specified language with enhanced security and error handling."""
        language = language.lower()
        timeout = timeout or self.max_execution_time
        
        if not self.is_language_supported(language):
            return {
                "success": False,
                "error": f"Language '{language}' is not supported or compiler not available",
                "stdout": "",
                "stderr": "",
                "return_code": -1
            }

        # Basic security check - prevent dangerous operations
        if self._contains_dangerous_code(code, language):
            return {
                "success": False,
                "error": "Code contains potentially dangerous operations",
                "stdout": "",
                "stderr": "Security check failed",
                "return_code": -1
            }

        # Check syntax first
        syntax_error = self.check_syntax(code, language)
        if syntax_error:
            return {
                "success": False,
                "error": f"Syntax Error: {syntax_error}",
                "stdout": "",
                "stderr": syntax_error,
                "return_code": -1
            }

        try:
            return self._execute_code(code, language, timeout)
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }

    def _contains_dangerous_code(self, code: str, language: str) -> bool:
        """Basic security check for dangerous operations."""
        dangerous_patterns = {
            "python": [
                r'\bos\.system\b', r'\bsubprocess\b', r'\beval\b', r'\bexec\b',
                r'\b__import__\b', r'\bopen\s*\(.*["\']w', r'\brmdir\b', r'\bunlink\b'
            ],
            "java": [
                r'\bRuntime\.getRuntime\b', r'\bProcessBuilder\b', r'\bSystem\.exit\b',
                r'\bFile.*delete\b', r'\bFiles\.delete\b'
            ],
            "go": [
                r'\bos\.Exec\b', r'\bos\.Remove\b', r'\bcmd\.Exec\b', r'\bos\.Exit\b'
            ],
            "c": [
                r'\bsystem\s*\(', r'\bexec\b', r'\bunlink\b', r'\bremove\b'
            ],
            "cpp": [
                r'\bsystem\s*\(', r'\bexec\b', r'\bunlink\b', r'\bremove\b',
                r'std::system'
            ]
        }
        
        patterns = dangerous_patterns.get(language, [])
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        return False

    def _execute_code(self, code: str, language: str, timeout: int) -> Dict[str, Any]:
        """Execute code for a specific language."""
        temp_dir = self._create_secure_temp_dir()
        
        try:
            if language == "python":
                return self._run_python(code, temp_dir, timeout)
            elif language == "go":
                return self._run_go(code, temp_dir, timeout)
            elif language == "java":
                return self._run_java(code, temp_dir, timeout)
            elif language in ["c", "cpp"]:
                return self._run_c_cpp(code, language, temp_dir, timeout)
            else:
                return {
                    "success": False,
                    "error": f"Execution for {language} not implemented",
                    "stdout": "",
                    "stderr": "",
                    "return_code": -1
                }
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _run_python(self, code: str, temp_dir: str, timeout: int) -> Dict[str, Any]:
        """Execute Python code."""
        temp_file = os.path.join(temp_dir, "main.py")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        python_cmd = self.available_compilers["python"]
        return self._execute_subprocess([python_cmd, temp_file], temp_dir, timeout)

    def _run_go(self, code: str, temp_dir: str, timeout: int) -> Dict[str, Any]:
        """Execute Go code."""
        temp_file = os.path.join(temp_dir, "main.go")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        return self._execute_subprocess(["go", "run", temp_file], temp_dir, timeout)

    def _run_java(self, code: str, temp_dir: str, timeout: int) -> Dict[str, Any]:
        """Execute Java code."""
        # Extract class name
        class_match = re.search(r'public\s+class\s+(\w+)', code)
        class_name = class_match.group(1) if class_match else "Main"
        
        temp_file = os.path.join(temp_dir, f"{class_name}.java")
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Compile first
        compile_result = self._execute_subprocess(
            ["javac", temp_file], temp_dir, timeout // 2
        )
        
        if not compile_result["success"]:
            return compile_result
        
        # Then run
        return self._execute_subprocess(["java", class_name], temp_dir, timeout)

    def _run_c_cpp(self, code: str, language: str, temp_dir: str, timeout: int) -> Dict[str, Any]:
        """Execute C/C++ code."""
        compiler = "gcc" if language == "c" else "g++"
        extension = ".c" if language == "c" else ".cpp"
        
        temp_file = os.path.join(temp_dir, f"main{extension}")
        output_file = os.path.join(temp_dir, "main")
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(code)
        
        # Compile first
        compile_result = self._execute_subprocess(
            [compiler, "-o", output_file, temp_file, "-lm"], temp_dir, timeout // 2
        )
        
        if not compile_result["success"]:
            return compile_result
        
        # Then run
        return self._execute_subprocess([output_file], temp_dir, timeout)

    def _execute_subprocess(self, command: List[str], cwd: str, timeout: int) -> Dict[str, Any]:
        """Execute a subprocess with proper error handling and security."""
        try:
            # Set resource limits if available (Unix systems)
            if hasattr(os, 'setrlimit'):
                import resource
                def set_limits():
                    # Limit CPU time
                    resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
                    # Limit memory to 256MB
                    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
                preexec_fn = set_limits
            else:
                preexec_fn = None
            
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                preexec_fn=preexec_fn
            )
            
            # Limit output size
            stdout = result.stdout[:self.max_output_size] if result.stdout else ""
            stderr = result.stderr[:self.max_output_size] if result.stderr else ""
            
            if len(result.stdout) > self.max_output_size:
                stdout += "\n[Output truncated - too long]"
            if len(result.stderr) > self.max_output_size:
                stderr += "\n[Error output truncated - too long]"
            
            return {
                "success": result.returncode == 0,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Execution timed out after {timeout} seconds",
                "stdout": "",
                "stderr": f"Process timed out after {timeout} seconds",
                "return_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}",
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }

    def format_code(self, code: str, language: str) -> Tuple[bool, str]:
        """Format code for better readability."""
        language = language.lower()
        
        try:
            if language == "python":
                return self._format_python_code(code)
            elif language == "go":
                return self._format_go_code(code)
            elif language == "java":
                return self._format_java_code(code)
            elif language in ["c", "cpp"]:
                return self._format_c_cpp_code(code, language)
            else:
                return False, f"Code formatting for {language} is not supported"
        except Exception as e:
            return False, f"Formatting error: {str(e)}"

    def _format_python_code(self, code: str) -> Tuple[bool, str]:
        """Format Python code using black or autopep8."""
        try:
            # Try black first (better formatter)
            if shutil.which("black"):
                temp_dir = self._create_secure_temp_dir()
                temp_file = os.path.join(temp_dir, "code.py")
                
                try:
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        f.write(code)
                    
                    result = subprocess.run(
                        ["black", "--quiet", temp_file],
                        timeout=10,
                        cwd=temp_dir
                    )
                    
                    if result.returncode == 0:
                        with open(temp_file, 'r', encoding='utf-8') as f:
                            return True, f.read()
                finally:
                    shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Fallback to autopep8
            import autopep8
            formatted_code = autopep8.fix_code(code, options={'aggressive': 1})
            return True, formatted_code
            
        except ImportError:
            return False, "Code formatting requires 'black' or 'autopep8'. Install with: pip install black autopep8"
        except Exception as e:
            return False, f"Python formatting error: {str(e)}"

    def _format_go_code(self, code: str) -> Tuple[bool, str]:
        """Format Go code using gofmt."""
        if not shutil.which("gofmt"):
            return False, "Go formatter 'gofmt' not found"
        
        try:
            result = subprocess.run(
                ["gofmt"],
                input=code,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, f"Go formatting error: {result.stderr}"
                
        except Exception as e:
            return False, f"Go formatting error: {str(e)}"

    def _format_java_code(self, code: str) -> Tuple[bool, str]:
        """Format Java code (basic indentation)."""
        # Basic Java formatting - you can integrate with google-java-format if needed
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            if not stripped:
                formatted_lines.append('')
                continue
            
            # Decrease indent for closing braces
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
            
            # Add the line with proper indentation
            formatted_lines.append('    ' * indent_level + stripped)
            
            # Increase indent for opening braces
            if stripped.endswith('{'):
                indent_level += 1
        
        return True, '\n'.join(formatted_lines)

    def _format_c_cpp_code(self, code: str, language: str) -> Tuple[bool, str]:
        """Format C/C++ code using clang-format if available."""
        if shutil.which("clang-format"):
            try:
                result = subprocess.run(
                    ["clang-format", "--style=Google"],
                    input=code,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return True, result.stdout
                else:
                    return False, f"clang-format error: {result.stderr}"
                    
            except Exception as e:
                return False, f"C/C++ formatting error: {str(e)}"
        else:
            return False, "C/C++ formatter 'clang-format' not found"

    def get_language_info(self, language: str) -> Dict[str, Any]:
        """Get comprehensive information about a programming language."""
        language = language.lower()
        
        if not language in self.supported_languages:
            return {"supported": False, "error": f"Language '{language}' is not supported"}
        
        is_available = language in self.available_compilers
        
        return {
            "supported": True,
            "available": is_available,
            "language": language,
            "file_extension": self.get_file_extension(language),
            "compiler_path": self.available_compilers.get(language, "Not found"),
            "syntax_checking_available": is_available,
            "formatting_available": is_available,
            "execution_available": is_available
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the system and available compilers."""
        return {
            "supported_languages": self.supported_languages,
            "available_compilers": self.available_compilers,
            "max_execution_time": self.max_execution_time,
            "max_output_size": self.max_output_size,
            "temp_directory": tempfile.gettempdir()
        }

    def validate_and_execute(self, code: str, language: str, timeout: int = None) -> Dict[str, Any]:
        """Validate syntax and execute code with comprehensive results."""
        # First validate syntax
        syntax_error = self.check_syntax(code, language)
        if syntax_error:
            return {
                "success": False,
                "syntax_valid": False,
                "syntax_error": syntax_error,
                "stdout": "",
                "stderr": syntax_error,
                "execution_attempted": False,
                "return_code": -1
            }
        
        # If syntax is valid, execute the code
        execution_result = self.run_code(code, language, timeout)
        
        return {
            "success": execution_result["success"],
            "syntax_valid": True,
            "syntax_error": None,
            "stdout": execution_result["stdout"],
            "stderr": execution_result["stderr"],
            "execution_attempted": True,
            "return_code": execution_result.get("return_code", -1),
            "error": execution_result.get("error")
        }


if __name__ == "__main__":
    compiler = CodeCompiler()
    
    