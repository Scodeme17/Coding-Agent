import re
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from phi.agent import Agent
from phi.model.groq import Groq
from dotenv import load_dotenv
import logging
from .coding_detect import CodingDetector
from .language_detect import LanguageDetector
from .code_analyzer import CodeAnalyzer
from .metrics import PerformanceMetrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

class CodingAgent:
    def __init__(self, temperature=0.2, max_tokens=16000):
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.agent = None
        self.chat_history = []
        
        # Initialize components
        self.coding_detector = CodingDetector()
        self.language_detector = LanguageDetector()
        self.code_analyzer = CodeAnalyzer()
        self.metrics = PerformanceMetrics()
        
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable is required")
        
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the AI agent with optimized instructions"""
        try:
            self.agent = Agent(
                model=Groq(
                    id="llama-3.3-70b-versatile",
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    api_key=self.groq_api_key
                ),
                instructions=self._get_system_instructions()
            )
            logger.info("Agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing agent: {e}")
            raise
    
    def _get_system_instructions(self) -> str:
        """Optimized system instructions for better performance"""
        return """You are an EXPERT CODING ASSISTANT with comprehensive knowledge across ALL programming domains.

CORE EXPERTISE:
• Languages: Python, Java, JavaScript, TypeScript, C/C++, Go, Rust, Kotlin, Swift, PHP, Ruby, Scala, Dart, R, MATLAB
• Web: React, Vue, Angular, Node.js, Django, Flask, Spring Boot, ASP.NET, Laravel, FastAPI
• Mobile: Android, iOS, Flutter, React Native, Xamarin
• Data/AI: Machine Learning, Deep Learning, Data Science, Computer Vision, NLP, TensorFlow, PyTorch
• Databases: SQL, NoSQL, MongoDB, PostgreSQL, MySQL, Redis, Elasticsearch
• Cloud/DevOps: AWS, Azure, GCP, Docker, Kubernetes, Jenkins, Terraform, Ansible
• Systems: Operating Systems, Networking, Distributed Systems, Microservices, Cybersecurity
• Algorithms: Data Structures, Competitive Programming, Optimization, Complexity Analysis

RESPONSE FORMAT:
1. Provide complete, working, production-ready code
2. Include comprehensive error handling
3. Add clear, concise comments for complex logic
4. Explain approach, time/space complexity
5. Suggest optimizations and alternatives
6. Include real-world usage examples
7. Format code with proper language specification

QUALITY STANDARDS:
• Write clean, maintainable, efficient code
• Follow language-specific best practices
• Implement proper error handling
• Consider security implications
• Optimize for performance when needed
• Provide multiple solutions when applicable
• Include testing strategies

Always format code using triple backticks with language specification."""

    def generate_optimized_solution(self, query: str) -> Dict[str, Any]:
        """Generate optimized solution with comprehensive analysis"""
        if not self.agent:
            return {
                'content': 'Error: AI agent not initialized.',
                'code_blocks': [],
                'success': False,
                'analysis': {},
                'alternatives': []
            }
        
        enhanced_query = f"""
CODING REQUEST: {query}

Provide:
1. Complete working solution with error handling
2. Time/space complexity analysis
3. Alternative approaches if applicable
4. Best practices and optimizations
5. Real-world usage examples
6. Edge cases handling

Format code with proper language specification in triple backticks.
"""
        
        try:
            self.metrics.update('queries_processed')
            start_time = time.time()
            
            response = self.agent.run(enhanced_query)
            
            processing_time = time.time() - start_time
            
            if hasattr(response, 'content'):
                response_content = response.content
            elif isinstance(response, str):
                response_content = response
            else:
                response_content = str(response)
            
            code_blocks = self.extract_code_blocks(response_content)
            
            analysis = {}
            real_time_issues = {}
            
            for i, block in enumerate(code_blocks):
                block_key = f'block_{i}'
                analysis[block_key] = self.code_analyzer.analyze_code_quality(block['code'], block['language'])
                real_time_issues[block_key] = self.code_analyzer.detect_real_time_issues(block['code'], block['language'])
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.chat_history.append({
                'timestamp': timestamp,
                'query': query,
                'response': response_content,
                'code_blocks': code_blocks,
                'analysis': analysis,
                'real_time_issues': real_time_issues,
                'processing_time': processing_time,
                'performance_metrics': self.metrics.get_metrics()
            })
            
            self.metrics.update('successful_responses')
            self.metrics.update('code_blocks_generated', len(code_blocks))
            
            logger.info(f"Query processed in {processing_time:.2f}s. Code blocks: {len(code_blocks)}")
            
            return {
                'content': response_content,
                'code_blocks': code_blocks,
                'success': True,
                'analysis': analysis,
                'real_time_issues': real_time_issues,
                'processing_time': processing_time,
                'suggestions': self._generate_improvement_suggestions(code_blocks, analysis)
            }
            
        except Exception as e:
            error_msg = f"Error processing query: {str(e)}"
            logger.error(error_msg)
            self.metrics.update('errors_detected')
            
            return {
                'content': error_msg,
                'code_blocks': [],
                'success': False,
                'analysis': {},
                'real_time_issues': {},
                'processing_time': 0
            }
    
    def _generate_improvement_suggestions(self, code_blocks: List[Dict], analysis: Dict) -> List[str]:
        """Generate improvement suggestions based on analysis"""
        suggestions = []
        
        for i, block in enumerate(code_blocks):
            block_analysis = analysis.get(f'block_{i}', {})
            complexity = block_analysis.get('complexity_score', 0)
            issues = block_analysis.get('issues', [])
            
            if complexity > 70:
                suggestions.append(f"Code block {i+1}: Consider breaking down complex logic into smaller functions")
            
            if len(issues) > 5:
                suggestions.append(f"Code block {i+1}: Multiple issues detected - review for code quality")
            
            if block_analysis.get('security_score', 10) < 7:
                suggestions.append(f"Code block {i+1}: Security concerns detected - review sensitive operations")
            
            if block['language'] == 'python' and len(block['code'].split('\n')) > 50:
                suggestions.append(f"Code block {i+1}: Consider using classes or modules for better organization")
        
        return suggestions
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Main query processing with enhanced categorization"""
        is_coding = self.coding_detector.is_coding_related(query)
        
        if is_coding:
            self.metrics.update('coding_queries')
            return self.generate_optimized_solution(query)
        else:
            self.metrics.update('non_coding_queries')
            return {
                'content': '''I specialize in coding and programming assistance. I can help with:

🔧 PROGRAMMING LANGUAGES
Python, Java, JavaScript, TypeScript, C/C++, Go, Rust, Kotlin, Swift, PHP, Ruby, Scala

🌐 WEB DEVELOPMENT
Frontend: React, Vue, Angular, HTML/CSS
Backend: Node.js, Django, Flask, Spring Boot, Express, FastAPI

📱 MOBILE DEVELOPMENT  
Android, iOS, Flutter, React Native, Xamarin

🤖 DATA SCIENCE & AI
Machine Learning, Deep Learning, Data Analysis, TensorFlow, PyTorch, Pandas, NumPy

🗄️ DATABASES & CLOUD
SQL, NoSQL, MongoDB, PostgreSQL, AWS, Azure, Docker, Kubernetes

🔒 CYBERSECURITY & SYSTEMS
Secure coding, System programming, Network programming, Cryptography

🏆 COMPETITIVE PROGRAMMING
Algorithms, Data Structures, LeetCode, Dynamic Programming, Graph Theory

🎮 GAME DEVELOPMENT
Unity, Unreal Engine, OpenGL, Game algorithms

Ask me any programming question - from basic syntax to advanced system design!''',
                'code_blocks': [],
                'success': False,
                'analysis': {},
                'real_time_issues': {},
                'is_coding_related': False
            }
    
    def extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """Enhanced code block extraction with better detection"""
        code_blocks = []
        
        pattern = r'```(\w+)?\n?(.*?)```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for lang, code in matches:
            if code.strip():
                cleaned_code = code.strip()
                detected_lang = lang.lower() if lang else self.language_detector.detect(cleaned_code)
                
                code_blocks.append({
                    'language': detected_lang,
                    'code': cleaned_code,
                    'length': len(cleaned_code.split('\n')),
                    'complexity': self.language_detector.estimate_complexity(cleaned_code),
                    'char_count': len(cleaned_code),
                    'estimated_time': self.language_detector.estimate_execution_time(cleaned_code, detected_lang)
                })
        
        if not code_blocks:
            inline_pattern = r'`([^`\n]{20,}[^`\n]*)`'
            inline_matches = re.findall(inline_pattern, text)
            for match in inline_matches:
                code_blocks.append({
                    'language': self.language_detector.detect(match),
                    'code': match.strip(),
                    'length': 1,
                    'complexity': 'low',
                    'char_count': len(match),
                    'estimated_time': 'instant'
                })
        
        return code_blocks
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Enhanced performance metrics"""
        return self.metrics.get_metrics()
    
    def export_analysis_report(self, filename: str) -> bool:
        """Export comprehensive analysis report"""
        return self.metrics.export_analysis_report(filename, self.chat_history)
    
    def clear_chat_history(self):
        """Clear chat history and reset metrics"""
        self.chat_history = []
        self.metrics.clear()
        logger.info("Chat history and metrics reset")
    
    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get enhanced chat history"""
        return self.chat_history
    
    def save_chat_history(self, filename: str) -> bool:
        """Save enhanced chat history"""
        return self.metrics.save_chat_history(filename, self.chat_history)
    
    def load_chat_history(self, filename: str) -> bool:
        """Load chat history from file"""
        return self.metrics.load_chat_history(filename, self.chat_history)