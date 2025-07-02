import re

class LanguageDetector:
    def __init__(self):
        self.patterns = self._init_language_patterns()
    
    def _init_language_patterns(self):
        return {
            'python': [
                r'def\s+\w+\s*\(', r'import\s+\w+', r'from\s+\w+\s+import', 
                r'print\s*\(', r'if\s+__name__\s*==\s*["\']__main__["\']',
                r'class\s+\w+\s*\(.*\):', r'self\.\w+', r'elif\s+', r'#.*'
            ],
            'java': [
                r'public\s+class\s+\w+', r'public\s+static\s+void\s+main',
                r'System\.out\.println', r'private\s+\w+', r'public\s+\w+',
                r'import\s+java\.', r'\bint\s+\w+\s*=', r'//.*'
            ],
            'javascript': [
                r'function\s+\w+\s*\(', r'const\s+\w+\s*=', r'let\s+\w+\s*=',
                r'console\.log', r'=>', r'var\s+\w+', r'document\.',
                r'window\.', r'/\*.*?\*/', r'//.*'
            ],
            'typescript': [
                r'interface\s+\w+', r'type\s+\w+\s*=', r':\s*\w+\s*=',
                r'public\s+\w+:', r'private\s+\w+:', r'export\s+(class|interface)',
                r'import.*from\s+["\']'
            ],
            'c': [
                r'#include\s*<\w+\.h>', r'int\s+main\s*\(', r'printf\s*\(',
                r'scanf\s*\(', r'malloc\s*\(', r'free\s*\(', r'/\*.*?\*/'
            ],
            'cpp': [
                r'#include\s*<iostream>', r'std::', r'cout\s*<<', r'cin\s*>>',
                r'class\s+\w+\s*{', r'public:', r'private:', r'namespace\s+\w+'
            ],
            'go': [
                r'package\s+main', r'func\s+main\s*\(', r'fmt\.Print',
                r'import\s+\(', r'var\s+\w+\s+\w+', r'func\s+\w+\s*\(',
                r'go\s+\w+\s*\('
            ],
            'rust': [
                r'fn\s+main\s*\(', r'println!', r'let\s+mut', r'let\s+\w+',
                r'impl\s+\w+', r'struct\s+\w+', r'enum\s+\w+', r'match\s+\w+'
            ],
            'sql': [
                r'SELECT\s+.*FROM', r'INSERT\s+INTO', r'UPDATE\s+\w+\s+SET',
                r'DELETE\s+FROM', r'CREATE\s+TABLE', r'ALTER\s+TABLE',
                r'DROP\s+TABLE', r'WHERE\s+\w+'
            ],
            'html': [
                r'<html>', r'<head>', r'<body>', r'<div>', r'<p>',
                r'<!DOCTYPE\s+html>', r'<script>', r'<style>'
            ],
            'css': [
                r'\.\w+\s*{', r'#\w+\s*{', r'\w+\s*{', r'@media',
                r'font-family:', r'background-color:', r'display:'
            ]
        }
    
    def detect(self, code: str) -> str:
        """Detect the programming language of a code snippet"""
        code_lower = code.lower()
        
        for lang, lang_patterns in self.patterns.items():
            score = sum(1 for pattern in lang_patterns 
                       if re.search(pattern, code, re.IGNORECASE | re.MULTILINE))
            if score >= 2:
                return lang
        
        # Fallback based on common keywords
        if any(keyword in code_lower for keyword in ['def ', 'import ', 'print(']):
            return 'python'
        elif any(keyword in code_lower for keyword in ['function', 'const ', 'let ']):
            return 'javascript'
        elif any(keyword in code_lower for keyword in ['public class', 'system.out']):
            return 'java'
        
        return 'python'
    
    def estimate_complexity(self, code: str) -> str:
        """Estimate code complexity with more sophisticated analysis"""
        lines = len([line for line in code.split('\n') if line.strip()])
        
        complexity_indicators = {
            'loops': len(re.findall(r'\b(for|while)\b', code, re.IGNORECASE)),
            'conditionals': len(re.findall(r'\b(if|else|elif|switch|case)\b', code, re.IGNORECASE)),
            'functions': len(re.findall(r'\b(def|function|func)\s+\w+', code, re.IGNORECASE)),
            'classes': len(re.findall(r'\b(class|struct|interface)\s+\w+', code, re.IGNORECASE)),
            'recursion': len(re.findall(r'\brecursive|\brecursion', code, re.IGNORECASE)),
            'async': len(re.findall(r'\b(async|await|promise|future)\b', code, re.IGNORECASE)),
            'nested_structures': len(re.findall(r'\{\s*\{|\[\s*\[|\(\s*\(', code))
        }
        
        complexity_score = (
            complexity_indicators['loops'] * 2 +
            complexity_indicators['conditionals'] * 1 +
            complexity_indicators['functions'] * 1.5 +
            complexity_indicators['classes'] * 2 +
            complexity_indicators['recursion'] * 3 +
            complexity_indicators['async'] * 2 +
            complexity_indicators['nested_structures'] * 1.5 +
            lines * 0.1
        )
        
        if complexity_score < 5:
            return 'low'
        elif complexity_score < 15:
            return 'medium'
        elif complexity_score < 30:
            return 'high'
        else:
            return 'very_high'
    
    def estimate_execution_time(self, code: str, language: str) -> str:
        """Estimate rough execution time category"""
        complexity = self.estimate_complexity(code)
        lines = len(code.split('\n'))
        
        # Simple heuristics based on complexity and language
        if complexity == 'low' and lines < 20:
            return 'instant'
        elif complexity == 'medium' and lines < 100:
            return 'fast'
        elif complexity == 'high' or lines > 200:
            return 'moderate'
        else:
            return 'slow'