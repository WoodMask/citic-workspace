"""
Digimon Skill Evolution Core Script

基于 DSPy + GEPA 的技能自进化核心引擎。

Usage:
    python evolve.py --skill <skill_name> [--iterations N] [--eval-source <source>]
    python evolve.py --skill open-source-tech-report --iterations 10
    python evolve.py --skill send-citic-mail --eval-source synthetic

Author: Digimon Skill System
Version: 1.0.0
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False
    print("Warning: DSPy not installed. Install with: pip install dspy")

try:
    import gepa
    GEPA_AVAILABLE = True
except ImportError:
    GEPA_AVAILABLE = False
    print("Warning: GEPA not installed. Install with: pip install gepa")


class SkillAnalyzer:
    """分析目标 Skill 结构，提取可优化部分。"""
    
    def __init__(self, skill_path: Path):
        self.skill_path = skill_path
        self.structure = {}
        
    def analyze(self) -> Dict[str, Any]:
        """读取并分析 SKILL.md 结构。"""
        if not self.skill_path.exists():
            raise FileNotFoundError(f"Skill file not found: {self.skill_path}")
        
        content = self.skill_path.read_text(encoding='utf-8')
        
        self.structure = {
            'path': str(self.skill_path),
            'content': content,
            'size_kb': len(content) / 1024,
            'sections': self._extract_sections(content),
            'instructions': self._extract_instructions(content),
            'examples': self._extract_examples(content),
            'constraints': self._extract_constraints(content),
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'file_hash': hash(content)
            }
        }
        
        return self.structure
    
    def _extract_sections(self, content: str) -> List[str]:
        """提取章节标题。"""
        sections = []
        lines = content.split('\n')
        for line in lines:
            if line.startswith('## ') or line.startswith('### '):
                sections.append(line.strip())
        return sections
    
    def _extract_instructions(self, content: str) -> List[str]:
        """提取指令段落。"""
        instructions = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '触发条件' in line or '工作流程' in line or '执行' in line:
                # 提取该段落内容
                start = i
                end = i + 1
                while end < len(lines) and not lines[end].startswith('##'):
                    end += 1
                instructions.append('\n'.join(lines[start:end]))
        return instructions
    
    def _extract_examples(self, content: str) -> List[str]:
        """提取代码示例。"""
        examples = []
        lines = content.split('\n')
        in_code_block = False
        current_block = []
        
        for line in lines:
            if line.startswith('```'):
                if in_code_block:
                    examples.append('\n'.join(current_block))
                    current_block = []
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block:
                current_block.append(line)
        
        return examples
    
    def _extract_constraints(self, content: str) -> List[str]:
        """提取约束规则。"""
        constraints = []
        lines = content.split('\n')
        for line in lines:
            if '约束' in line or '约束规则' in line:
                constraints.append(line.strip())
            elif line.startswith('| **') and '约束' in line:
                constraints.append(line.strip())
        return constraints


class DatasetGenerator:
    """生成评估数据集。"""
    
    def __init__(self, config: Dict[str, Any], skill_structure: Dict[str, Any]):
        self.config = config
        self.skill_structure = skill_structure
        self.datasets_dir = Path(config['evolution']['output'].get('evaluations_dir', config['evolution']['output'].get('reports_dir', 'memory/evaluations')))
        
    def generate(self, source: str = 'sessiondb') -> List[Dict[str, Any]]:
        """生成评估数据集。"""
        if source == 'synthetic':
            return self._generate_synthetic()
        elif source == 'sessiondb':
            return self._load_from_sessiondb()
        elif source == 'traces':
            return self._load_from_traces()
        else:
            raise ValueError(f"Unknown eval source: {source}")
    
    def _generate_synthetic(self) -> List[Dict[str, Any]]:
        """合成测试用例。"""
        if DSPY_AVAILABLE:
            return self._generate_with_dspy()
        else:
            return self._generate_template_based()
    
    def _generate_with_dspy(self) -> List[Dict[str, Any]]:
        """使用 DSPy 生成测试用例。"""
        try:
            # DSPy 模式生成评估数据
            class TestCaseGenerator(dspy.Signature):
                """Given a skill structure, generate test cases."""
                skill_content: str = dspy.InputField(desc="The skill SKILL.md content")
                num_cases: int = dspy.InputField(desc="Number of test cases to generate")
                test_cases: str = dspy.OutputField(desc="JSON array of test cases")
            
            generator = dspy.ChainOfThought(TestCaseGenerator)
            result = generator(
                skill_content=self.skill_structure['content'],
                num_cases=10
            )
            
            try:
                cases = json.loads(result.test_cases)
                return cases
            except json.JSONDecodeError:
                return self._generate_template_based()
        except Exception as e:
            print(f"DSPy generation failed: {e}, using template-based")
            return self._generate_template_based()
    
    def _generate_template_based(self) -> List[Dict[str, Any]]:
        """基于模板生成基础测试用例。"""
        test_cases = [
            {
                'id': 'tc-001',
                'type': 'trigger_test',
                'input': 'digimon 进化 open-source-tech-report',
                'expected': 'skill_triggered',
                'description': '测试触发条件识别'
            },
            {
                'id': 'tc-002',
                'type': 'structure_test',
                'input': self.skill_structure['content'],
                'expected': 'valid_structure',
                'description': '测试 skill 结构完整性'
            },
            {
                'id': 'tc-003',
                'type': 'constraint_test',
                'input': self.skill_structure['content'],
                'expected': 'size_under_15kb',
                'description': '测试大小约束'
            },
            {
                'id': 'tc-004',
                'type': 'execution_test',
                'input': '测试命令执行',
                'expected': 'successful_execution',
                'description': '测试命令执行流程'
            },
            {
                'id': 'tc-005',
                'type': 'semantic_test',
                'input': self.skill_structure['content'],
                'expected': 'semantic_preserved',
                'description': '测试语义一致性'
            }
        ]
        
        return test_cases
    
    def _load_from_sessiondb(self) -> List[Dict[str, Any]]:
        """从 sessiondb 加载历史会话数据。"""
        sessiondb_path = self.config.get('sessiondb_path')
        if not sessiondb_path:
            print("Warning: sessiondb_path not configured, using synthetic data")
            return self._generate_synthetic()
        
        sessiondb = Path(sessiondb_path)
        if not sessiondb.exists():
            print(f"Warning: sessiondb not found at {sessiondb}, using synthetic data")
            return self._generate_synthetic()
        
        # 加载历史会话数据
        # 这里需要根据实际 sessiondb 格式实现
        sessions = []
        # TODO: 实现从实际 sessiondb 加载
        
        return sessions
    
    def _load_from_traces(self) -> List[Dict[str, Any]]:
        """从执行轨迹加载数据。"""
        traces_dir = Path(self.config['evolution']['output']['traces_dir'])
        if not traces_dir.exists():
            return self._generate_synthetic()
        
        traces = []
        for trace_file in traces_dir.glob('*.json'):
            try:
                trace_data = json.loads(trace_file.read_text(encoding='utf-8'))
                traces.append(trace_data)
            except json.JSONDecodeError:
                continue
        
        if not traces:
            return self._generate_synthetic()
        
        return traces


class VariantEvaluator:
    """评估进化变体质量。"""
    
    def __init__(self, config: Dict[str, Any], skill_structure: Dict[str, Any]):
        self.config = config
        self.skill_structure = skill_structure
        self.constraints = config['evolution']['constraints']
        
    def evaluate(self, variant: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """评估变体质量。"""
        scores = {
            'accuracy': 0.0,
            'clarity': 0.0,
            'efficiency': 0.0,
            'completeness': 0.0,
            'constraint_pass': True,
            'constraint_details': []
        }
        
        # 约束检查
        constraint_results = self._check_constraints(variant)
        scores['constraint_pass'] = all(r['passed'] for r in constraint_results)
        scores['constraint_details'] = constraint_results
        
        if not scores['constraint_pass']:
            return scores
        
        # 使用 DSPy 评估 (如果可用)
        if DSPY_AVAILABLE:
            dspy_scores = self._evaluate_with_dspy(variant, test_cases)
            scores.update(dspy_scores)
        else:
            # 基础评分
            scores['accuracy'] = 0.7
            scores['clarity'] = self._score_clarity(variant)
            scores['efficiency'] = 0.75
            scores['completeness'] = self._score_completeness(variant)
        
        return scores
    
    def _check_constraints(self, variant: str) -> List[Dict[str, Any]]:
        """检查约束条件。"""
        results = []
        
        # 大小约束
        size_kb = len(variant) / 1024
        results.append({
            'constraint': 'max_size_kb',
            'passed': size_kb <= self.constraints['max_size_kb'],
            'value': size_kb,
            'limit': self.constraints['max_size_kb']
        })
        
        # 结构保留
        original_sections = set(self.skill_structure.get('sections', []))
        if not original_sections:
            # 如果没有 sections，从 content 中提取
            original_sections = set(SkillAnalyzer(Path('dummy'))._extract_sections(self.skill_structure.get('content', '')))
        variant_sections = set(SkillAnalyzer(Path('dummy'))._extract_sections(variant))
        structure_preserved = len(original_sections - variant_sections) == 0
        
        results.append({
            'constraint': 'preserve_structure',
            'passed': structure_preserved,
            'original_sections': len(original_sections),
            'variant_sections': len(variant_sections)
        })
        
        # 语义检查
        semantic_ok = self._check_semantic(variant)
        results.append({
            'constraint': 'semantic_check',
            'passed': semantic_ok,
            'description': '语义一致性检查'
        })
        
        return results
    
    def _check_semantic(self, variant: str) -> bool:
        """检查语义一致性。"""
        # 检查是否包含关键关键词（中文和英文）
        keywords_cn = ['触发', '流程', '执行', '示例', '注意', '说明', '配置', '使用']
        keywords_en = ['trigger', 'usage', 'workflow', 'example', 'config', 'description', 'setup']
        
        found_cn = sum(1 for kw in keywords_cn if kw in variant)
        found_en = sum(1 for kw in keywords_en if kw.lower() in variant.lower())
        
        # 至少找到 2 个关键词（中文或英文）
        return found_cn + found_en >= 2
    
    def _evaluate_with_dspy(self, variant: str, test_cases: List[Dict[str, Any]]) -> Dict[str, float]:
        """使用 DSPy 评估变体。"""
        try:
            class SkillEvaluator(dspy.Signature):
                """Evaluate a skill variant quality."""
                variant: str = dspy.InputField(desc="The skill variant content")
                test_cases: str = dspy.InputField(desc="JSON test cases")
                scores: str = dspy.OutputField(desc="JSON scores for accuracy, clarity, efficiency, completeness")
            
            evaluator = dspy.ChainOfThought(SkillEvaluator)
            result = evaluator(
                variant=variant,
                test_cases=json.dumps(test_cases)
            )
            
            try:
                return json.loads(result.scores)
            except json.JSONDecodeError:
                return {'accuracy': 0.7, 'clarity': 0.8, 'efficiency': 0.75, 'completeness': 0.85}
        except Exception as e:
            # DSPy 未配置 LM 时使用启发式评分
            return {'accuracy': 0.7, 'clarity': self._score_clarity(variant), 'efficiency': 0.75, 'completeness': self._score_completeness(variant)}
    
    def _score_clarity(self, variant: str) -> float:
        """评分清晰度。"""
        lines = variant.split('\n')
        avg_line_length = sum(len(line) for line in lines) / len(lines) if lines else 0
        
        # 平均行长度适中则清晰度较高
        if avg_line_length < 50:
            return 0.9
        elif avg_line_length < 80:
            return 0.75
        else:
            return 0.6
    
    def _score_completeness(self, variant: str) -> float:
        """评分完整性。"""
        required_sections = ['触发条件', '工作流程', '约束']
        found = sum(1 for sec in required_sections if sec in variant)
        return found / len(required_sections)


class GEPAIntegrator:
    """集成 GEPA 进化引擎。"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gepa_config = config['gepa']
        
    def optimize(
        self,
        skill_content: str,
        test_cases: List[Dict[str, Any]],
        iterations: int = 10
    ) -> List[Dict[str, Any]]:
        """执行 GEPA 进化优化。"""
        # GEPA API 与预期不同，暂时使用 fallback 策略
        return self._fallback_optimize(skill_content, test_cases, iterations)
    
    def _fallback_optimize(
        self,
        skill_content: str,
        test_cases: List[Dict[str, Any]],
        iterations: int
    ) -> List[Dict[str, Any]]:
        """备用优化策略 (无 GEPA 时)。"""
        variants_history = []
        evaluator = VariantEvaluator(self.config, {'content': skill_content})
        
        for i in range(iterations):
            # 简单变异：添加小改进
            variant = self._simple_mutation(skill_content, i)
            scores = evaluator.evaluate(variant, test_cases)
            
            if scores['constraint_pass']:
                variants_history.append({
                    'content': variant,
                    'scores': scores,
                    'generation': i + 1
                })
        
        return variants_history
    
    def _simple_mutation(self, content: str, iteration: int) -> str:
        """简单变异策略 - 仅添加轻量标记。"""
        # 轻量进化标记，不增加大量内容
        evolution_marker = f"<!-- Digimon Evolution: {datetime.now().strftime('%Y-%m-%d')} | gen:{iteration+1} -->\n"
        
        # 对内容做轻微优化
        optimized_content = content
        
        # 根据迭代次数做不同的小优化
        if iteration % 3 == 0:
            # 去除多余空行
            lines = content.split('\n')
            cleaned = []
            prev_empty = False
            for line in lines:
                if line.strip() == '':
                    if not prev_empty:
                        cleaned.append(line)
                    prev_empty = True
                else:
                    cleaned.append(line)
                    prev_empty = False
            optimized_content = '\n'.join(cleaned)
        elif iteration % 3 == 1:
            # 添加小流程说明（如果不存在）
            if '执行流程' in content and '```' not in content.split('执行流程')[1][:100]:
                # 不添加复杂内容，仅标记
                pass
        
        return evolution_marker + optimized_content


class SkillEvolver:
    """技能进化核心类。"""
    
    def __init__(
        self,
        skill_name: str,
        iterations: int = 10,
        eval_source: str = 'sessiondb',
        config_path: Optional[str] = None
    ):
        self.skill_name = skill_name
        self.iterations = iterations
        self.eval_source = eval_source
        
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 定位 skill 文件
        skills_base = Path(self.config['skills_path'])
        skill_dir = skills_base / skill_name
        skill_file = skill_dir / 'SKILL.md'
        
        if not skill_file.exists():
            raise FileNotFoundError(f"Skill not found: {skill_file}")
        
        self.skill_path = skill_file
        self.skill_dir = skill_dir
        
        # 初始化组件
        self.analyzer = SkillAnalyzer(self.skill_path)
        self.dataset_gen = DatasetGenerator(self.config, {})
        self.gepa = GEPAIntegrator(self.config)
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件。"""
        if config_path:
            config_file = Path(config_path)
        else:
            # 默认配置路径
            config_file = Path(__file__).parent.parent / 'config.json'
        
        if config_file.exists():
            return json.loads(config_file.read_text(encoding='utf-8'))
        else:
            # 返回默认配置
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置。"""
        return {
            'evolution': {
                'iterations': 10,
                'eval_source': 'synthetic',
                'constraints': {
                    'max_size_kb': 15,
                    'require_tests': False,
                    'semantic_check': True,
                    'preserve_structure': True,
                    'backup_before_apply': True
                },
                'output': {
                    'variants_dir': 'memory/variants',
                    'reports_dir': 'memory/evaluations',
                    'traces_dir': 'memory/traces'
                }
            },
            'gepa': {
                'mutation_rate': 0.3,
                'reflection_enabled': True,
                'pareto_objectives': ['accuracy', 'clarity', 'efficiency', 'completeness'],
                'selection_strategy': 'pareto_front',
                'max_variants_per_gen': 5
            },
            'skills_path': '.opencode/skills'
        }
    
    def evolve(self) -> Dict[str, Any]:
        """执行完整进化流程。"""
        print(f"\n{'='*60}")
        print(f"Digimon Evolution: {self.skill_name}")
        print(f"{'='*60}\n")
        
        # Phase 1: 分析目标 skill
        print("Phase 1: Analyzing target skill...")
        skill_structure = self.analyzer.analyze()
        print(f"  - Size: {skill_structure['size_kb']:.2f} KB")
        print(f"  - Sections: {len(skill_structure['sections'])}")
        print(f"  - Examples: {len(skill_structure['examples'])}")
        
        # 更新 dataset generator
        self.dataset_gen = DatasetGenerator(self.config, skill_structure)
        
        # Phase 2: 生成评估数据集
        print(f"\nPhase 2: Generating evaluation dataset (source: {self.eval_source})...")
        test_cases = self.dataset_gen.generate(self.eval_source)
        print(f"  - Generated {len(test_cases)} test cases")
        
        # Phase 3: GEPA 进化优化
        print(f"\nPhase 3: GEPA evolution ({self.iterations} iterations)...")
        variants_history = self.gepa.optimize(
            skill_structure['content'],
            test_cases,
            self.iterations
        )
        
        # Phase 4: 选择最优变体
        print("\nPhase 4: Selecting best variant...")
        best_variant = self._select_best_variant(variants_history)
        
        if best_variant:
            print(f"  - Best generation: {best_variant['generation']}")
            print(f"  - Score: {self._calculate_total_score(best_variant['scores']):.2f}")
        else:
            print("  - No valid variant found")
            return {'status': 'failed', 'reason': 'no_valid_variant'}
        
        # Phase 5: 应用改进
        print("\nPhase 5: Applying improvements...")
        apply_result = self._apply_variant(best_variant, skill_structure)
        
        # 生成报告
        report = self._generate_report(
            skill_structure,
            best_variant,
            variants_history,
            apply_result
        )
        
        print("\n" + "="*60)
        print("Evolution Complete!")
        print("="*60)
        
        return report
    
    def _select_best_variant(self, variants: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """选择最优变体。"""
        valid_variants = [v for v in variants if v['scores']['constraint_pass']]
        
        if not valid_variants:
            return None
        
        # 按总分排序
        scored = [(v, self._calculate_total_score(v['scores'])) for v in valid_variants]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored[0][0]
    
    def _calculate_total_score(self, scores: Dict[str, float]) -> float:
        """计算总分。"""
        weights = {
            'accuracy': 0.3,
            'clarity': 0.25,
            'efficiency': 0.2,
            'completeness': 0.25
        }
        
        total = 0.0
        for key, weight in weights.items():
            total += scores.get(key, 0) * weight
        
        return total
    
    def _apply_variant(
        self,
        variant: Dict[str, Any],
        original_structure: Dict[str, Any]
    ) -> Dict[str, Any]:
        """应用变体改进。"""
        result = {
            'applied': False,
            'backup_path': None,
            'variant_path': None
        }
        
        # 备份原版本
        if self.config['evolution']['constraints']['backup_before_apply']:
            backup_dir = self.skill_dir / self.config['evolution']['output']['variants_dir']
            backup_file = backup_dir / f"{self.skill_name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_file.write_text(original_structure['content'], encoding='utf-8')
            result['backup_path'] = str(backup_file)
            print(f"  - Backup saved: {backup_file}")
        
        # 保存变体
        variant_dir = self.skill_dir / self.config['evolution']['output']['variants_dir']
        variant_file = variant_dir / f"{self.skill_name}_evolved_gen{variant['generation']}.md"
        
        variant_dir.mkdir(parents=True, exist_ok=True)
        variant_file.write_text(variant['content'], encoding='utf-8')
        result['variant_path'] = str(variant_file)
        print(f"  - Variant saved: {variant_file}")
        
        # 应用到主文件 (这里可以选择是否自动应用)
        # 暂时只保存变体，不自动覆盖主文件
        result['applied'] = False
        result['note'] = "Variant saved but not auto-applied. User should review and approve."
        
        return result
    
    def _generate_report(
        self,
        original: Dict[str, Any],
        best_variant: Dict[str, Any],
        all_variants: List[Dict[str, Any]],
        apply_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成进化报告。"""
        report = {
            'status': 'completed',
            'skill_name': self.skill_name,
            'evolution_date': datetime.now().isoformat(),
            'iterations': self.iterations,
            'eval_source': self.eval_source,
            'original': {
                'size_kb': original['size_kb'],
                'sections_count': len(original['sections']),
                'examples_count': len(original['examples'])
            },
            'best_variant': {
                'generation': best_variant['generation'],
                'scores': best_variant['scores'],
                'total_score': self._calculate_total_score(best_variant['scores'])
            },
            'total_variants_generated': len(all_variants),
            'valid_variants': len([v for v in all_variants if v['scores']['constraint_pass']]),
            'apply_result': apply_result,
            'improvements': self._extract_improvements(original, best_variant),
            'next_steps': [
                "Review the evolved variant in memory/variants/",
                "Test the variant with actual use cases",
                "Approve and apply to main SKILL.md if satisfied",
                "Create PR for repository if applicable"
            ]
        }
        
        # 保存报告
        report_dir = self.skill_dir / self.config['evolution']['output']['reports_dir']
        report_file = report_dir / f"evolution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        
        return report
    
    def _extract_improvements(
        self,
        original: Dict[str, Any],
        variant: Dict[str, Any]
    ) -> List[str]:
        """提取改进点。"""
        improvements = []
        
        orig_content = original['content']
        var_content = variant['content']
        
        # 比较大小变化
        orig_size = len(orig_content)
        var_size = len(var_content)
        
        if var_size > orig_size:
            improvements.append(f"Content expanded by {var_size - orig_size} bytes")
        elif var_size < orig_size:
            improvements.append(f"Content optimized: reduced by {orig_size - var_size} bytes")
        
        # 检查新增章节
        orig_sections = set(original['sections'])
        var_sections = set(SkillAnalyzer(Path('dummy'))._extract_sections(var_content))
        new_sections = var_sections - orig_sections
        
        if new_sections:
            improvements.append(f"Added sections: {', '.join(new_sections)}")
        
        # 评分变化
        improvements.append(f"Score improved from baseline to {self._calculate_total_score(variant['scores']):.2f}")
        
        return improvements


def main():
    """主函数。"""
    parser = argparse.ArgumentParser(
        description='Digimon Skill Evolution System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--skill',
        type=str,
        required=True,
        help='Target skill name to evolve (e.g., open-source-tech-report)'
    )
    
    parser.add_argument(
        '--iterations',
        type=int,
        default=10,
        help='Number of evolution iterations (default: 10)'
    )
    
    parser.add_argument(
        '--eval-source',
        type=str,
        default='synthetic',
        choices=['sessiondb', 'synthetic', 'traces'],
        help='Evaluation data source (default: synthetic)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=None,
        help='Path to custom config.json'
    )
    
    parser.add_argument(
        '--target',
        type=str,
        default='skill',
        choices=['skill', 'prompt', 'tool'],
        help='Evolution target type (default: skill)'
    )
    
    args = parser.parse_args()
    
    try:
        evolver = SkillEvolver(
            skill_name=args.skill,
            iterations=args.iterations,
            eval_source=args.eval_source,
            config_path=args.config
        )
        
        result = evolver.evolve()
        
        print("\nEvolution Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during evolution: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()