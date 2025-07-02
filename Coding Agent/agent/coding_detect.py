import re

class CodingDetector:
    def __init__(self):
        self.coding_keywords = self._init_coding_keywords()
        self.code_patterns = self._init_code_patterns()
    
    def _init_coding_keywords(self):
        """Initialize comprehensive coding keywords for faster lookup"""
        return {
            # Core programming
            'algorithm', 'code', 'function', 'method', 'class', 'object', 'variable', 'loop', 'array',
            'string', 'integer', 'boolean', 'float', 'debug', 'test', 'optimization', 'recursion',
            'iteration', 'conditional', 'exception', 'error', 'bug', 'syntax', 'compile', 'runtime',
            
            # Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift',
            'php', 'ruby', 'scala', 'dart', 'r', 'matlab', 'perl', 'shell', 'bash', 'powershell',
            'sql', 'html', 'css', 'xml', 'json', 'yaml', 'dockerfile', 'makefile',
            
            # Frameworks & Libraries
            'react', 'vue', 'angular', 'node', 'express', 'django', 'flask', 'spring', 'fastapi',
            'nextjs', 'nuxt', 'svelte', 'bootstrap', 'tailwind', 'jquery', 'redux', 'axios',
            'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scipy', 'matplotlib', 'opencv',
            'sklearn', 'nltk', 'spacy', 'requests', 'beautifulsoup', 'selenium', 'pytest',
            
            # Technologies
            'api', 'rest', 'graphql', 'websocket', 'http', 'https', 'tcp', 'udp', 'json', 'xml',
            'database', 'mysql', 'postgresql', 'mongodb', 'redis', 'sqlite', 'orm', 'crud',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'jenkins', 'gitlab', 'github',
            'terraform', 'ansible', 'microservices', 'serverless', 'lambda', 'container',
            
            # Mobile & Game Dev
            'android', 'ios', 'flutter', 'react-native', 'xamarin', 'unity', 'unreal',
            'opengl', 'directx', 'vulkan', 'metal', 'shader', 'physics', 'render',
            
            # Data & AI
            'machine-learning', 'deep-learning', 'neural-network', 'ai', 'ml', 'dl', 'nlp',
            'computer-vision', 'data-science', 'analytics', 'statistics', 'regression',
            'classification', 'clustering', 'recommendation', 'model', 'training', 'inference',
            
            # Security & Crypto
            'security', 'encryption', 'cryptography', 'hash', 'authentication', 'authorization',
            'oauth', 'jwt', 'ssl', 'tls', 'vulnerability', 'penetration', 'firewall',
            'blockchain', 'cryptocurrency', 'smart-contract', 'web3', 'defi', 'nft',
            
            # System & DevOps
            'linux', 'unix', 'windows', 'kernel', 'process', 'thread', 'memory', 'cpu',
            'network', 'socket', 'file-system', 'operating-system', 'distributed',
            'load-balancer', 'cache', 'cdn', 'monitoring', 'logging', 'metrics',
            
            # Competitive Programming
            'leetcode', 'hackerrank', 'codeforces', 'codechef', 'topcoder', 'atcoder',
            'dynamic-programming', 'greedy', 'graph', 'tree', 'heap', 'stack', 'queue',
            'binary-search', 'sorting', 'hashing', 'bit-manipulation', 'segment-tree',
            'disjoint-set', 'trie', 'suffix', 'knapsack', 'shortest-path', 'mst',
            
            # Software Engineering
            'design-pattern', 'architecture', 'solid', 'dry', 'kiss', 'refactor',
            'version-control', 'git', 'svn', 'merge', 'branch', 'commit', 'pull-request',
            'agile', 'scrum', 'kanban', 'tdd', 'bdd', 'cicd', 'devops', 'sre',
            
            # Web Development
            'frontend', 'backend', 'fullstack', 'responsive', 'mobile-first', 'spa',
            'pwa', 'ssr', 'ssg', 'seo', 'accessibility', 'performance', 'lighthouse',
            'webpack', 'babel', 'eslint', 'prettier', 'jest', 'cypress', 'storybook',
            
            # Data Structures
            'linked-list', 'binary-tree', 'avl-tree', 'red-black-tree', 'b-tree',
            'hash-table', 'priority-queue', 'disjoint-set', 'bloom-filter', 'lru-cache'
        }
    
    def _init_code_patterns(self):
        """Initialize regex patterns for code detection"""
        return [
            r'\b(def|function|class|import|include|using|namespace|package)\b',
            r'\b(if|else|elif|for|while|switch|case|try|catch|finally)\b',
            r'\b(int|string|float|double|char|bool|var|let|const)\b',
            r'\b(public|private|protected|static|final|abstract)\b',
            r'\b(return|throw|new|delete|malloc|free)\b',
            r'[{}();]',
            r'\b\w+\s*\([^)]*\)\s*[{;]',
            r'\b[A-Z][a-zA-Z]*Error\b',
            r'\b(print|console\.log|System\.out\.println|cout|printf)\b',
            r'[<>=!]=?|[+\-*/%]=?|\+\+|--',
            r'\b0x[0-9a-fA-F]+\b',
            r'//.*$|/\*.*?\*/|#.*$',
            r'\b(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b',
            r'<[^>]+>.*?</[^>]+>',
            r'\$\{[^}]+\}',
            r'@\w+',
            r'\b\w+::\w+\b',
            r'\b[a-zA-Z_]\w*\.[a-zA-Z_]\w*\b'
        ]
    
    def is_coding_related(self, query: str) -> bool:
        """Enhanced coding detection with multiple strategies"""
        query_lower = query.lower().replace('-', '').replace('_', '')
        
        # Strategy 1: Direct keyword matching (fastest)
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        if query_words & self.coding_keywords:
            return True
        
        # Strategy 2: Compound terms and phrases
        coding_phrases = [
            'how to', 'write code', 'implement', 'create function', 'solve problem',
            'algorithm for', 'data structure', 'time complexity', 'space complexity',
            'best practice', 'design pattern', 'code review', 'unit test', 'integration test',
            'api call', 'web scraping', 'file handling', 'database query', 'sort array',
            'reverse string', 'find element', 'binary search', 'merge sort', 'quick sort',
            'linked list', 'binary tree', 'hash table', 'dynamic programming', 'greedy algorithm',
            'graph traversal', 'shortest path', 'minimum spanning tree', 'topological sort',
            'string matching', 'pattern matching', 'regular expression', 'state machine',
            'compile error', 'runtime error', 'syntax error', 'logic error', 'memory leak',
            'performance optimization', 'code optimization', 'refactoring', 'code smell',
            'clean code', 'solid principles', 'design patterns', 'mvc pattern', 'mvp pattern',
            'microservices architecture', 'monolithic architecture', 'event driven',
            'asynchronous programming', 'concurrent programming', 'parallel programming',
            'thread safety', 'race condition', 'deadlock', 'mutex', 'semaphore',
            'load balancing', 'caching strategy', 'database optimization', 'query optimization',
            'web development', 'mobile development', 'game development', 'desktop application',
            'machine learning model', 'neural network', 'deep learning', 'data analysis',
            'web scraping', 'api integration', 'cloud deployment', 'container orchestration'
        ]
        
        for phrase in coding_phrases:
            if phrase in query_lower:
                return True
        
        # Strategy 3: Code pattern matching
        for pattern in self.code_patterns:
            if re.search(pattern, query, re.IGNORECASE | re.MULTILINE):
                return True
        
        # Strategy 4: File extensions and formats
        file_extensions = [
            '.py', '.java', '.js', '.ts', '.cpp', '.c', '.h', '.cs', '.go', '.rs',
            '.php', '.rb', '.scala', '.kt', '.swift', '.dart', '.r', '.m', '.pl',
            '.sh', '.bash', '.ps1', '.sql', '.html', '.css', '.xml', '.json', '.yaml',
            '.dockerfile', '.makefile', '.gradle', '.maven', '.npm', '.pip', '.cargo'
        ]
        
        for ext in file_extensions:
            if ext in query_lower:
                return True
        
        # Strategy 5: Programming concepts and terminology
        advanced_concepts = [
            'big o notation', 'computational complexity', 'asymptotic analysis',
            'divide and conquer', 'backtracking', 'branch and bound', 'memoization',
            'tabulation', 'sliding window', 'two pointers', 'fast and slow pointers',
            'union find', 'disjoint set', 'fenwick tree', 'segment tree', 'trie',
            'suffix array', 'kmp algorithm', 'rabin karp', 'z algorithm', 'manacher',
            'dijkstra', 'bellman ford', 'floyd warshall', 'prim', 'kruskal',
            'ford fulkerson', 'edmonds karp', 'dinic', 'push relabel', 'bipartite matching',
            'strongly connected components', 'topological sorting', 'articulation points',
            'bridges', 'euler path', 'hamiltonian path', 'traveling salesman',
            'knapsack problem', 'longest common subsequence', 'edit distance',
            'palindrome partitioning', 'matrix chain multiplication', 'coin change',
            'rod cutting', 'subset sum', 'partition problem', 'word break',
            'wildcard matching', 'regular expression matching', 'interleaving string'
        ]
        
        for concept in advanced_concepts:
            if concept in query_lower:
                return True
        
        # Strategy 6: Technology stack combinations
        tech_stacks = [
            'mean stack', 'mern stack', 'lamp stack', 'django rest', 'spring boot',
            'react native', 'vue nuxt', 'angular material', 'bootstrap jquery',
            'tensorflow keras', 'pytorch lightning', 'pandas numpy', 'flask sqlalchemy',
            'express mongoose', 'rails activerecord', 'laravel eloquent', 'aspnet core',
            'docker kubernetes', 'aws lambda', 'azure functions', 'gcp cloud functions',
            'jenkins gitlab', 'terraform ansible', 'prometheus grafana', 'elk stack',
            'redis mongodb', 'postgresql mysql', 'cassandra elasticsearch', 'kafka zookeeper'
        ]
        
        for stack in tech_stacks:
            if stack in query_lower:
                return True
        
        # Strategy 7: Error messages and debugging
        error_patterns = [
            r'error.*undefined', r'cannot.*resolve', r'module.*not.*found',
            r'syntax.*error', r'indentation.*error', r'name.*error', r'type.*error',
            r'attribute.*error', r'index.*error', r'key.*error', r'value.*error',
            r'connection.*refused', r'timeout.*error', r'permission.*denied',
            r'access.*denied', r'file.*not.*found', r'directory.*not.*found',
            r'null.*pointer', r'segmentation.*fault', r'stack.*overflow',
            r'heap.*overflow', r'memory.*leak', r'out.*of.*memory',
            r'compilation.*failed', r'build.*failed', r'test.*failed',
            r'assertion.*failed', r'exception.*thrown', r'unhandled.*exception'
        ]
        
        for pattern in error_patterns:
            if re.search(pattern, query_lower):
                return True
        
        # Strategy 8: Question patterns common in coding
        coding_question_patterns = [
            r'how\s+to\s+(implement|create|build|write|code)',
            r'what\s+is\s+(algorithm|data\s+structure|design\s+pattern)',
            r'explain\s+(recursion|dynamic\s+programming|greedy)',
            r'difference\s+between\s+\w+\s+and\s+\w+',
            r'best\s+way\s+to\s+(sort|search|optimize)',
            r'time\s+complexity\s+of',
            r'space\s+complexity\s+of',
            r'how\s+does\s+\w+\s+work',
            r'when\s+to\s+use\s+\w+',
            r'pros\s+and\s+cons\s+of',
            r'compare\s+\w+\s+(vs|and)\s+\w+',
            r'which\s+is\s+better',
            r'performance\s+comparison',
            r'benchmark\s+\w+',
            r'optimize\s+\w+\s+for',
            r'improve\s+performance\s+of',
            r'reduce\s+time\s+complexity',
            r'memory\s+efficient',
            r'scalable\s+solution',
            r'distributed\s+system'
        ]
        
        for pattern in coding_question_patterns:
            if re.search(pattern, query_lower):
                return True
        
        return False