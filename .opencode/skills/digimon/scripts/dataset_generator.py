"""
Dataset Generator Module

生成评估数据集，支持多种来源：
- sessiondb: 真实会话历史
- synthetic: 合成测试用例
- traces: 执行轨迹分析
"""

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False


class SyntheticDataGenerator:
    """合成测试用例生成器。"""
    
    def __init__(self, skill_structure: Dict[str, Any]):
        self.skill_structure = skill_structure
        
    def generate_test_cases(self, num_cases: int = 10) -> List[Dict[str, Any]]:
        """生成合成测试用例。"""
        if DSPY_AVAILABLE:
            return self._generate_with_dspy(num_cases)
        else:
            return self._generate_template_based(num_cases)
    
    def _generate_with_dspy(self, num_cases: int) -> List[Dict[str, Any]]:
        """使用 DSPy 生成测试用例。"""
        class TestCaseSignature(dspy.Signature):
            skill_content: str = dspy.InputField(desc="Skill content to analyze")
            num_cases: int = dspy.InputField(desc="Number of cases to generate")
            test_cases_json: str = dspy.OutputField(desc="JSON array of test cases")
        
        generator = dspy.ChainOfThought(TestCaseSignature)
        result = generator(
            skill_content=self.skill_structure['content'],
            num_cases=num_cases
        )
        
        try:
            return json.loads(result.test_cases_json)
        except json.JSONDecodeError:
            return self._generate_template_based(num_cases)
    
    def _generate_template_based(self, num_cases: int) -> List[Dict[str, Any]]:
        """基于模板生成测试用例。"""
        templates = self._get_templates()
        
        test_cases = []
        for i in range(num_cases):
            template = random.choice(templates)
            test_case = {
                'id': f'stc-{i+1:03d}',
                'type': template['type'],
                'input': template['input_template'],
                'expected': template['expected'],
                'description': template['description'],
                'priority': template['priority'],
                'created_at': datetime.now().isoformat()
            }
            test_cases.append(test_case)
        
        return test_cases
    
    def _get_templates(self) -> List[Dict[str, Any]]:
        """获取测试用例模板。"""
        return [
            {
                'type': 'trigger_test',
                'input_template': 'digimon 进化 target_skill',
                'expected': 'skill_triggered_correctly',
                'description': '测试触发条件识别是否正确',
                'priority': 'high'
            },
            {
                'type': 'structure_test',
                'input_template': 'SKILL.md content validation',
                'expected': 'valid_structure_with_required_sections',
                'description': '测试 skill 结构完整性',
                'priority': 'high'
            },
            {
                'type': 'constraint_test',
                'input_template': 'constraint validation check',
                'expected': 'all_constraints_passed',
                'description': '测试约束规则检查',
                'priority': 'high'
            },
            {
                'type': 'size_test',
                'input_template': 'file size check',
                'expected': 'size_within_limit',
                'description': '测试文件大小约束',
                'priority': 'medium'
            },
            {
                'type': 'semantic_test',
                'input_template': 'semantic consistency check',
                'expected': 'semantic_preserved',
                'description': '测试语义一致性',
                'priority': 'medium'
            },
            {
                'type': 'execution_test',
                'input_template': 'execute skill workflow',
                'expected': 'successful_execution',
                'description': '测试执行流程完整性',
                'priority': 'medium'
            },
            {
                'type': 'integration_test',
                'input_template': 'integrate with other skills',
                'expected': 'successful_integration',
                'description': '测试与其他 skill 集成',
                'priority': 'low'
            },
            {
                'type': 'edge_case_test',
                'input_template': 'edge case handling',
                'expected': 'edge_case_handled_correctly',
                'description': '测试边缘情况处理',
                'priority': 'low'
            }
        ]


class SessionDBLoader:
    """从 sessiondb 加载历史会话数据。"""
    
    def __init__(self, sessiondb_path: Path):
        self.sessiondb_path = sessiondb_path
        
    def load_sessions(self) -> List[Dict[str, Any]]:
        """加载历史会话数据。"""
        if not self.sessiondb_path.exists():
            return []
        
        sessions = []
        
        # 支持多种 sessiondb 格式
        if self.sessiondb_path.is_file():
            # 单文件 sessiondb
            try:
                data = json.loads(self.sessiondb_path.read_text(encoding='utf-8'))
                if isinstance(data, list):
                    sessions = data
                elif isinstance(data, dict) and 'sessions' in data:
                    sessions = data['sessions']
            except json.JSONDecodeError:
                pass
        else:
            # 目录形式 sessiondb
            for session_file in self.sessiondb_path.glob('*.json'):
                try:
                    session_data = json.loads(session_file.read_text(encoding='utf-8'))
                    sessions.append(session_data)
                except json.JSONDecodeError:
                    continue
        
        return sessions
    
    def extract_test_cases(self, sessions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从会话中提取测试用例。"""
        test_cases = []
        
        for i, session in enumerate(sessions):
            # 提取会话中的成功和失败案例
            if 'success' in session:
                test_case = {
                    'id': f'sdb-{i+1:03d}',
                    'type': 'real_session',
                    'input': session.get('input', ''),
                    'expected': session.get('success', True) ? 'success' : 'failure',
                    'description': f"Session from {session.get('timestamp', 'unknown')}",
                    'priority': 'high',
                    'source': 'sessiondb'
                }
                test_cases.append(test_case)
        
        return test_cases


class TraceAnalyzerLoader:
    """从执行轨迹加载评估数据。"""
    
    def __init__(self, traces_dir: Path):
        self.traces_dir = traces_dir
        
    def load_traces(self) -> List[Dict[str, Any]]:
        """加载执行轨迹。"""
        if not self.traces_dir.exists():
            return []
        
        traces = []
        for trace_file in self.traces_dir.glob('*.json'):
            try:
                trace_data = json.loads(trace_file.read_text(encoding='utf-8'))
                traces.append(trace_data)
            except json.JSONDecodeError:
                continue
        
        return traces
    
    def extract_failure_patterns(self, traces: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """从轨迹中提取失败模式。"""
        patterns = []
        
        for i, trace in enumerate(traces):
            if trace.get('status') == 'failed':
                pattern = {
                    'id': f'trc-{i+1:03d}',
                    'type': 'failure_pattern',
                    'input': trace.get('input', ''),
                    'expected': 'avoid_failure',
                    'root_cause': trace.get('error', 'unknown'),
                    'description': f"Failure pattern from trace",
                    'priority': 'high',
                    'source': 'traces'
                }
                patterns.append(pattern)
        
        return patterns


def generate_dataset(
    skill_structure: Dict[str, Any],
    source: str,
    output_dir: Path,
    num_cases: int = 10
) -> List[Dict[str, Any]]:
    """生成评估数据集的统一入口。"""
    
    test_cases = []
    
    if source == 'synthetic':
        generator = SyntheticDataGenerator(skill_structure)
        test_cases = generator.generate_test_cases(num_cases)
        
    elif source == 'sessiondb':
        # 需要配置 sessiondb_path
        sessiondb_path = skill_structure.get('config', {}).get('sessiondb_path')
        if sessiondb_path:
            loader = SessionDBLoader(Path(sessiondb_path))
            sessions = loader.load_sessions()
            test_cases = loader.extract_test_cases(sessions)
            
            # 如果没有足够数据，补充合成数据
            if len(test_cases) < num_cases:
                synthetic = SyntheticDataGenerator(skill_structure)
                test_cases.extend(synthetic.generate_test_cases(num_cases - len(test_cases)))
        else:
            synthetic = SyntheticDataGenerator(skill_structure)
            test_cases = synthetic.generate_test_cases(num_cases)
            
    elif source == 'traces':
        traces_dir = output_dir / 'traces'
        loader = TraceAnalyzerLoader(traces_dir)
        traces = loader.load_traces()
        test_cases = loader.extract_failure_patterns(traces)
        
        # 补充合成数据
        if len(test_cases) < num_cases:
            synthetic = SyntheticDataGenerator(skill_structure)
            test_cases.extend(synthetic.generate_test_cases(num_cases - len(test_cases)))
    
    # 保存数据集
    dataset_file = output_dir / f'dataset_{source}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    dataset_file.parent.mkdir(parents=True, exist_ok=True)
    dataset_file.write_text(json.dumps(test_cases, indent=2, ensure_ascii=False), encoding='utf-8')
    
    return test_cases


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate evaluation dataset')
    parser.add_argument('--source', default='synthetic', choices=['synthetic', 'sessiondb', 'traces'])
    parser.add_argument('--num', type=int, default=10)
    parser.add_argument('--output', default='memory/evaluations')
    
    args = parser.parse_args()
    
    # 示例 skill structure
    example_structure = {
        'content': 'Example skill content',
        'sections': ['Trigger', 'Workflow'],
        'examples': []
    }
    
    test_cases = generate_dataset(
        example_structure,
        args.source,
        Path(args.output),
        args.num
    )
    
    print(f"Generated {len(test_cases)} test cases")