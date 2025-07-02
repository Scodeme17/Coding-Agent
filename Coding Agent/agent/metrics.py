import json
from datetime import datetime
from typing import Dict, List, Any

class PerformanceMetrics:
    def __init__(self):
        self.metrics = {
            'queries_processed': 0,
            'successful_responses': 0,
            'code_blocks_generated': 0,
            'errors_detected': 0,
            'coding_queries': 0,
            'non_coding_queries': 0
        }
        self.code_analysis_cache = {}
    
    def update(self, key: str, value: int = 1):
        if key in self.metrics:
            self.metrics[key] += value
    
    def get_metrics(self) -> Dict[str, Any]:
        total_queries = self.metrics['queries_processed']
        success_rate = (self.metrics['successful_responses'] / max(1, total_queries)) * 100
        
        return {
            **self.metrics,
            'success_rate': round(success_rate, 2),
            'cache_size': len(self.code_analysis_cache)
        }
    
    def clear(self):
        self.metrics = {
            'queries_processed': 0,
            'successful_responses': 0,
            'code_blocks_generated': 0,
            'errors_detected': 0,
            'coding_queries': 0,
            'non_coding_queries': 0
        }
        self.code_analysis_cache = {}
    
    def export_analysis_report(self, filename: str, chat_history: List) -> bool:
        try:
            report = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'agent_version': '3.0',
                    'total_sessions': len(chat_history)
                },
                'performance_metrics': self.get_metrics(),
                'detailed_analysis': [],
                'code_quality_summary': self._generate_quality_summary(chat_history),
                'recommendations': self._generate_recommendations()
            }
            
            for entry in chat_history:
                report['detailed_analysis'].append({
                    'timestamp': entry['timestamp'],
                    'query_length': len(entry['query']),
                    'response_length': len(entry['response']),
                    'code_blocks_count': len(entry.get('code_blocks', [])),
                    'processing_time': entry.get('processing_time', 0),
                })
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            return False
    
    def _generate_quality_summary(self, chat_history: List) -> Dict[str, Any]:
        all_analyses = []
        for entry in chat_history:
            if 'analysis' in entry:
                all_analyses.extend(entry['analysis'].values())
        
        if not all_analyses:
            return {}
        
        avg_complexity = sum(a.get('complexity_score', 0) for a in all_analyses) / len(all_analyses)
        avg_security = sum(a.get('security_score', 10) for a in all_analyses) / len(all_analyses)
        
        return {
            'average_complexity_score': round(avg_complexity, 2),
            'average_security_score': round(avg_security, 2),
            'total_issues_found': sum(len(a.get('issues', [])) for a in all_analyses),
            'total_suggestions_made': sum(len(a.get('suggestions', [])) for a in all_analyses)
        }
    
    def _generate_recommendations(self) -> List[str]:
        recommendations = []
        metrics = self.get_metrics()
        
        if metrics['coding_query_ratio'] < 80:
            recommendations.append("Consider focusing queries on coding-specific topics for better assistance")
        
        if metrics['success_rate'] < 90:
            recommendations.append("Try providing more specific requirements in your queries")
        
        return recommendations
    
    def save_chat_history(self, filename: str, chat_history: List) -> bool:
        try:
            export_data = {
                'chat_history': chat_history,
                'performance_metrics': self.get_metrics(),
                'export_timestamp': datetime.now().isoformat(),
                'agent_version': '3.0'
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            return False
    
    def load_chat_history(self, filename: str, chat_history: List) -> bool:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'chat_history' in data:
                chat_history.clear()
                chat_history.extend(data['chat_history'])
            
            if 'performance_metrics' in data:
                saved_metrics = data['performance_metrics']
                for key in self.metrics:
                    if key in saved_metrics:
                        self.metrics[key] = saved_metrics[key]
            
            return True
        except Exception as e:
            return False