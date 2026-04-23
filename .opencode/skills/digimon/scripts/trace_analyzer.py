"""
Trace Analyzer Module

分析执行轨迹，提取失败模式和改进点。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class ExecutionTrace:
    """执行轨迹数据结构。"""
    
    def __init__(
        self,
        skill_name: str,
        input: str,
        output: str,
        status: str,
        error: Optional[str] = None,
        duration: Optional[float] = None,
        timestamp: Optional[str] = None
    ):
        self.skill_name = skill_name
        self.input = input
        self.output = output
        self.status = status
        self.error = error
        self.duration = duration
        self.timestamp = timestamp or datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'skill_name': self.skill_name,
            'input': self.input,
            'output': self.output,
            'status': self.status,
            'error': self.error,
            'duration': self.duration,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionTrace':
        return cls(
            skill_name=data.get('skill_name', 'unknown'),
            input=data.get('input', ''),
            output=data.get('output', ''),
            status=data.get('status', 'unknown'),
            error=data.get('error'),
            duration=data.get('duration'),
            timestamp=data.get('timestamp')
        )


class TraceCollector:
    """执行轨迹收集器。"""
    
    def __init__(self, traces_dir: Path):
        self.traces_dir = traces_dir
        self.traces_dir.mkdir(parents=True, exist_ok=True)
        
    def collect(self, trace: ExecutionTrace) -> str:
        """收集执行轨迹。"""
        trace_id = f"{trace.skill_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        trace_file = self.traces_dir / f"{trace_id}.json"
        
        trace_file.write_text(
            json.dumps(trace.to_dict(), indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        return str(trace_file)
    
    def load_all(self) -> List[ExecutionTrace]:
        """加载所有轨迹。"""
        traces = []
        
        for trace_file in self.traces_dir.glob('*.json'):
            try:
                data = json.loads(trace_file.read_text(encoding='utf-8'))
                traces.append(ExecutionTrace.from_dict(data))
            except json.JSONDecodeError:
                continue
        
        return traces


class FailureAnalyzer:
    """失败分析器。"""
    
    def analyze(self, traces: List[ExecutionTrace]) -> List[Dict[str, Any]]:
        """分析失败模式。"""
        failures = [t for t in traces if t.status == 'failed']
        
        patterns = []
        
        for failure in failures:
            pattern = self._extract_failure_pattern(failure)
            patterns.append(pattern)
        
        # 聚合相似失败
        aggregated = self._aggregate_patterns(patterns)
        
        return aggregated
    
    def _extract_failure_pattern(self, trace: ExecutionTrace) -> Dict[str, Any]:
        """提取失败模式。"""
        return {
            'skill_name': trace.skill_name,
            'input_type': self._classify_input(trace.input),
            'error_category': self._classify_error(trace.error),
            'error_message': trace.error,
            'timestamp': trace.timestamp,
            'frequency': 1
        }
    
    def _classify_input(self, input: str) -> str:
        """分类输入类型。"""
        if '进化' in input or 'evolve' in input.lower():
            return 'evolution_command'
        elif '生成' in input or 'generate' in input.lower():
            return 'generation_command'
        elif '查询' in input or 'search' in input.lower():
            return 'query_command'
        else:
            return 'other'
    
    def _classify_error(self, error: Optional[str]) -> str:
        """分类错误类型。"""
        if not error:
            return 'unknown'
        
        error_lower = error.lower()
        
        if 'filenotfound' in error_lower or 'not found' in error_lower:
            return 'resource_missing'
        elif 'timeout' in error_lower:
            return 'timeout'
        elif 'permission' in error_lower or 'access' in error_lower:
            return 'permission_error'
        elif 'syntax' in error_lower or 'parse' in error_lower:
            return 'syntax_error'
        elif 'constraint' in error_lower:
            return 'constraint_violation'
        elif 'memory' in error_lower:
            return 'memory_issue'
        else:
            return 'other'
    
    def _aggregate_patterns(self, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """聚合相似模式。"""
        aggregated = {}
        
        for pattern in patterns:
            key = f"{pattern['skill_name']}_{pattern['error_category']}"
            
            if key not in aggregated:
                aggregated[key] = pattern
            else:
                aggregated[key]['frequency'] += 1
        
        return list(aggregated.values())


class ImprovementExtractor:
    """改进建议提取器。"""
    
    def extract(self, failure_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从失败模式中提取改进建议。"""
        improvements = []
        
        for pattern in failure_patterns:
            suggestion = self._generate_improvement(pattern)
            if suggestion:
                improvements.append(suggestion)
        
        return improvements
    
    def _generate_improvement(self, pattern: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """生成改进建议。"""
        error_category = pattern['error_category']
        
        suggestions = {
            'resource_missing': {
                'type': 'skill_update',
                'action': '添加资源检查和备选方案',
                'priority': 'high',
                'details': '在 skill 中添加资源存在性检查，提供备选路径'
            },
            'timeout': {
                'type': 'skill_update',
                'action': '添加超时处理和重试机制',
                'priority': 'medium',
                'details': '在 skill 中设置合理的超时阈值和重试策略'
            },
            'permission_error': {
                'type': 'skill_update',
                'action': '添加权限检查提示',
                'priority': 'high',
                'details': '在 skill 中添加权限检查步骤和错误提示'
            },
            'syntax_error': {
                'type': 'skill_update',
                'action': '增强输入验证',
                'priority': 'medium',
                'details': '添加输入格式验证和预处理逻辑'
            },
            'constraint_violation': {
                'type': 'constraint_update',
                'action': '放宽或调整约束条件',
                'priority': 'medium',
                'details': '分析约束失败原因，考虑放宽限制或增加灵活性'
            },
            'memory_issue': {
                'type': 'skill_update',
                'action': '优化内存使用',
                'priority': 'medium',
                'details': '分批处理大数据，添加内存监控'
            }
        }
        
        suggestion = suggestions.get(error_category)
        
        if suggestion:
            suggestion['pattern'] = pattern
            suggestion['skill_target'] = pattern['skill_name']
            
        return suggestion


class TraceToDatasetConverter:
    """轨迹转评估数据集转换器。"""
    
    def convert(self, traces: List[ExecutionTrace]) -> List[Dict[str, Any]]:
        """将轨迹转换为评估数据集。"""
        test_cases = []
        
        for i, trace in enumerate(traces):
            test_case = {
                'id': f'ttc-{i+1:03d}',
                'type': 'trace_based',
                'input': trace.input,
                'expected': 'success' if trace.status == 'success' else 'avoid_failure',
                'actual_result': trace.status,
                'error': trace.error,
                'description': f"Based on trace from {trace.timestamp}",
                'priority': 'high' if trace.status == 'failed' else 'medium',
                'source': 'traces'
            }
            test_cases.append(test_case)
        
        return test_cases


def analyze_traces(traces_dir: Path) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """分析轨迹的统一入口。"""
    
    collector = TraceCollector(traces_dir)
    traces = collector.load_all()
    
    if not traces:
        return [], []
    
    # 失败分析
    analyzer = FailureAnalyzer()
    failure_patterns = analyzer.analyze(traces)
    
    # 改进建议
    extractor = ImprovementExtractor()
    improvements = extractor.extract(failure_patterns)
    
    return failure_patterns, improvements


def convert_traces_to_dataset(traces_dir: Path) -> List[Dict[str, Any]]:
    """将轨迹转换为评估数据集。"""
    
    collector = TraceCollector(traces_dir)
    traces = collector.load_all()
    
    converter = TraceToDatasetConverter()
    test_cases = converter.convert(traces)
    
    return test_cases


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Trace Analyzer')
    parser.add_argument('--traces-dir', default='memory/traces')
    parser.add_argument('--action', default='analyze', choices=['analyze', 'convert'])
    
    args = parser.parse_args()
    
    traces_dir = Path(args.traces_dir)
    
    if args.action == 'analyze':
        patterns, improvements = analyze_traces(traces_dir)
        print(f"Failure patterns: {len(patterns)}")
        print(f"Improvements: {len(improvements)}")
        
        for imp in improvements:
            print(f"  - {imp['action']} (priority: {imp['priority']})")
    
    elif args.action == 'convert':
        test_cases = convert_traces_to_dataset(traces_dir)
        print(f"Generated {len(test_cases)} test cases")