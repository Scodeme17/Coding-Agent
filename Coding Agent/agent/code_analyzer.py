import re
import ast
from typing import Dict, Any, List

class CodeAnalyzer:
    def analyze_code_quality(self, code: str, language: str) -> Dict[str, Any]:
        """Streamlined code quality analysis"""
        analysis = {
            'issues': [],
            'suggestions': [],
            'complexity_score': 0,
            'maintainability': 'Good',
            'security_score': 10,
            'performance_score': 8
        }
        
        try:
            if language.lower() == 'python':
                analysis.update(self._analyze_python_code(code))
            elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                analysis.update(self._analyze_javascript_code(code))
            elif language.lower() in ['java']:
                analysis.update(self._analyze_java_code(code))
            elif language.lower() in ['c', 'cpp', 'c++']:
                analysis.update(self._analyze_c_cpp_code(code))
            
            analysis['complexity_score'] = self._calculate_complexity_score(code, language)
            analysis['maintainability'] = self._assess_maintainability(analysis)
            
        except Exception as e:
            pass
        
        return analysis
    
    def _analyze_python_code(self, code: str) -> Dict[str, Any]:
        """Python-specific code analysis"""
        issues = []
        suggestions = []
        security_score = 10
        
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.name) < 3 and node.name not in ['x', 'y', 'z', 'i', 'j', 'k']:
                        issues.append(f"Consider more descriptive name for function '{node.name}'")
                    if len(node.args.args) > 5:
                        suggestions.append(f"Function '{node.name}' has many parameters, consider using dataclass or dict")
                
                elif isinstance(node, ast.For):
                    for child in ast.walk(node):
                        if isinstance(child, ast.For) and child != node:
                            suggestions.append("Nested loops detected - consider optimization")
                            break
        
        except SyntaxError as e:
            issues.append(f"Syntax error: {e}")
            security_score = 0
        
        # Security checks
        security_patterns = [
            (r'eval\s*\(', 3, "eval() is dangerous"),
            (r'exec\s*\(', 3, "exec() is dangerous"),
            (r'import\s+os.*system', 2, "os.system() can be unsafe"),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', 2, "shell=True can be dangerous"),
            (r'pickle\.loads?\s*\(', 2, "pickle can execute arbitrary code"),
        ]
        
        for pattern, severity, message in security_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                security_score -= severity
                issues.append(f"Security: {message}")
        
        # Best practices
        if 'import *' in code:
            issues.append("Avoid wildcard imports")
        if re.search(r'except\s*:', code):
            issues.append("Avoid bare except clauses")
        if 'global ' in code:
            suggestions.append("Consider avoiding global variables")
        
        return {
            'issues': issues,
            'suggestions': suggestions,
            'security_score': max(0, security_score)
        }
    
    def _analyze_javascript_code(self, code: str) -> Dict[str, Any]:
        """JavaScript/TypeScript code analysis"""
        issues = []
        suggestions = []
        
        # Common issues
        if '==' in code and '===' not in code:
            suggestions.append("Use strict equality (===) instead of loose equality (==)")
        if 'var ' in code:
            suggestions.append("Use 'let' or 'const' instead of 'var'")
        if re.search(r'innerHTML\s*=.*\+', code):
            issues.append("Potential XSS vulnerability with innerHTML concatenation")
        if 'eval(' in code:
            issues.append("eval() is dangerous and should be avoided")
        
        # Performance suggestions
        if re.search(r'document\.getElementById.*loop', code, re.DOTALL):
            suggestions.append("Cache DOM queries outside loops")
        if re.search(r'for\s*\(.*\.length', code):
            suggestions.append("Cache array length in for loops")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _analyze_java_code(self, code: str) -> Dict[str, Any]:
        """Java code analysis"""
        issues = []
        suggestions = []
        
        if 'System.out.println' in code and 'main(' not in code:
            suggestions.append("Consider using logging instead of System.out.println")
        if '== null' in code:
            suggestions.append("Consider using Objects.equals() or Optional")
        if re.search(r'catch\s*\([^)]*Exception[^)]*\)\s*\{\s*\}', code):
            issues.append("Empty catch blocks should be avoided")
        if 'String +' in code:
            suggestions.append("Use StringBuilder for string concatenation in loops")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _analyze_c_cpp_code(self, code: str) -> Dict[str, Any]:
        """C/C++ code analysis"""
        issues = []
        suggestions = []
        
        if 'malloc(' in code and 'free(' not in code:
            issues.append("Potential memory leak - malloc without free")
        if 'strcpy(' in code:
            issues.append("strcpy is unsafe - use strncpy or strcpy_s")
        if 'gets(' in code:
            issues.append("gets() is unsafe - use fgets()")
        if 'sprintf(' in code:
            suggestions.append("Consider using snprintf() for buffer safety")
        
        return {'issues': issues, 'suggestions': suggestions}
    
    def _calculate_complexity_score(self, code: str, language: str) -> int:
        """Calculate complexity score based on various factors"""
        lines = len(code.split('\n'))
        
        complexity_indicators = [
            r'for\s*\(', r'while\s*\(', r'if\s*\(', r'else\s+if', r'switch\s*\(',
            r'try\s*\{', r'catch\s*\(', r'finally\s*\{', r'class\s+\w+',
            r'function\s+\w+', r'def\s+\w+', r'async\s+', r'await\s+',
            r'Promise\s*\(', r'callback\s*\(', r'=>', r'map\s*\(', r'filter\s*\(',
            r'reduce\s*\(', r'forEach\s*\(', r'recursion', r'recursive'
        ]
        
        complexity_count = sum(len(re.findall(pattern, code, re.IGNORECASE)) 
                             for pattern in complexity_indicators)
        
        # Normalize complexity score
        base_score = min(complexity_count, 20)
        line_penalty = max(0, (lines - 50) // 10)
        return min(base_score + line_penalty, 100)
    
    def _assess_maintainability(self, analysis: Dict[str, Any]) -> str:
        """Assess code maintainability"""
        issues_count = len(analysis.get('issues', []))
        complexity = analysis.get('complexity_score', 0)
        
        if issues_count > 10 or complexity > 80:
            return 'Poor'
        elif issues_count > 5 or complexity > 50:
            return 'Fair'
        elif issues_count > 2 or complexity > 30:
            return 'Good'
        else:
            return 'Excellent'
    
    def detect_real_time_issues(self, code: str, language: str) -> List[Dict[str, str]]:
        """Detect issues in real-time with enhanced patterns"""
        issues = []
        
        # Universal patterns
        universal_patterns = [
            (r'TODO|FIXME|XXX|HACK', 'warning', 'TODO/FIXME comments found'),
            (r'console\.log\s*\(|print\s*\(.*debug', 'info', 'Debug statements detected'),
            (r'password\s*[=:]\s*["\'][^"\']{3,}["\']', 'security', 'Hardcoded password'),
            (r'api[_-]?key\s*[=:]\s*["\'][^"\']{10,}["\']', 'security', 'Hardcoded API key'),
            (r'secret\s*[=:]\s*["\'][^"\']{8,}["\']', 'security', 'Hardcoded secret'),
            (r'token\s*[=:]\s*["\'][^"\']{20,}["\']', 'security', 'Hardcoded token'),
        ]
        
        for pattern, issue_type, message in universal_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    'type': issue_type,
                    'message': message,
                    'line': line_num,
                    'column': match.start() - code.rfind('\n', 0, match.start())
                })
        
        # Language-specific patterns
        if language.lower() == 'python':
            issues.extend(self._detect_python_specific_issues(code))
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            issues.extend(self._detect_js_specific_issues(code))
        elif language.lower() == 'java':
            issues.extend(self._detect_java_specific_issues(code))
        
        return issues
    
    def _detect_python_specific_issues(self, code: str) -> List[Dict[str, str]]:
        """Python-specific issue detection"""
        issues = []
        python_patterns = [
            (r'except\s*:', 'warning', 'Bare except clause'),
            (r'import\s+\*', 'warning', 'Wildcard import'),
            (r'eval\s*\(', 'error', 'Dangerous eval() usage'),
            (r'exec\s*\(', 'error', 'Dangerous exec() usage'),
            (r'assert\s+', 'info', 'Assert statement (removed in production)'),
            (r'global\s+\w+', 'warning', 'Global variable usage'),
        ]
        
        for pattern, issue_type, message in python_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    'type': issue_type,
                    'message': message,
                    'line': line_num,
                    'column': match.start() - code.rfind('\n', 0, match.start())
                })
        
        return issues
    
    def _detect_js_specific_issues(self, code: str) -> List[Dict[str, str]]:
        """JavaScript-specific issue detection"""
        issues = []
        js_patterns = [
            (r'==(?!=)', 'warning', 'Use strict equality (===)'),
            (r'var\s+', 'info', 'Consider let/const instead of var'),
            (r'innerHTML\s*=.*\+', 'security', 'Potential XSS with innerHTML'),
            (r'eval\s*\(', 'error', 'Dangerous eval() usage'),
            (r'document\.write\s*\(', 'warning', 'document.write is deprecated'),
        ]
        
        for pattern, issue_type, message in js_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    'type': issue_type,
                    'message': message,
                    'line': line_num,
                    'column': match.start() - code.rfind('\n', 0, match.start())
                })
        
        return issues
    
    def _detect_java_specific_issues(self, code: str) -> List[Dict[str, str]]:
        """Java-specific issue detection"""
        issues = []
        java_patterns = [
            (r'System\.out\.print', 'info', 'Consider using logging'),
            (r'catch\s*\([^)]*\)\s*\{\s*\}', 'warning', 'Empty catch block'),
            (r'String\s+\w+\s*=\s*[^;]+\+', 'performance', 'String concatenation in loop'),
            (r'== null', 'warning', 'Consider using Objects.equals()'),
        ]
        
        for pattern, issue_type, message in java_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                line_num = code[:match.start()].count('\n') + 1
                issues.append({
                    'type': issue_type,
                    'message': message,
                    'line': line_num,
                    'column': match.start() - code.rfind('\n', 0, match.start())
                })
        
        return issues