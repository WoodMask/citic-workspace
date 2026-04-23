"""
GEPA Optimizer Integration Module

集成 GEPA (Genetic-Pareto Prompt Evolution) 进化引擎。
"""

import json
import random
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

try:
    from gepa import GEPAOptimizer as RealGEPAOptimizer
    GEPA_AVAILABLE = True
except ImportError:
    GEPA_AVAILABLE = False

from evaluator import ParetoSelector


class MutationStrategy:
    """变异策略。"""
    
    def __init__(self, mutation_rate: float = 0.3):
        self.mutation_rate = mutation_rate
        
    def mutate(self, content: str) -> str:
        """对内容进行变异。"""
        mutations = [
            self._simplify_section,
            self._reorder_sections,
            self._expand_instruction,
            self._add_example,
            self._clarify_constraint,
            self._optimize_flow
        ]
        
        # 随机选择变异操作
        selected_mutations = random.sample(
            mutations,
            k=int(len(mutations) * self.mutation_rate) + 1
        )
        
        result = content
        for mutation in selected_mutations:
            result = mutation(result)
        
        return result
    
    def _simplify_section(self, content: str) -> str:
        """简化章节内容。"""
        lines = content.split('\n')
        simplified = []
        
        for line in lines:
            # 简化过长的行
            if len(line) > 100 and not line.startswith('```'):
                # 尝试拆分
                if '|' in line:
                    # 表格行不拆分
                    simplified.append(line)
                else:
                    simplified.append(line[:80])
                    simplified.append(line[80:])
            else:
                simplified.append(line)
        
        return '\n'.join(simplified)
    
    def _reorder_sections(self, content: str) -> str:
        """调整章节顺序（仅轻微调整）。"""
        lines = content.split('\n')
        
        # 找到章节位置
        section_indices = []
        for i, line in enumerate(lines):
            if line.startswith('## '):
                section_indices.append(i)
        
        if len(section_indices) < 2:
            return content
        
        # 轻微调整相邻章节顺序
        # 注意：不破坏关键章节顺序
        return content
    
    def _expand_instruction(self, content: str) -> str:
        """扩展指令说明。"""
        # 在关键指令后添加简要说明
        pattern = r'(\## 触发条件\n)'
        replacement = r'\1\n> 说明：以下条件触发此技能执行。\n'
        
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content, count=1)
        
        return content
    
    def _add_example(self, content: str) -> str:
        """添加示例。"""
        if '示例' not in content and 'Example' not in content:
            example_section = """
## 使用示例

### 基本用法

```bash
digimon 进化 target-skill --iterations 10
```

### 进阶用法

```bash
digimon 进化 target-skill --eval-source sessiondb --iterations 15
```
"""
            # 在末尾添加
            content = content + '\n' + example_section
        
        return content
    
    def _clarify_constraint(self, content: str) -> str:
        """澄清约束说明。"""
        pattern = r'(\## 约束规则\n)'
        clarification = r'\1\n> 注意：以下约束为强制检查项，必须全部通过。\n'
        
        if re.search(pattern, content):
            content = re.sub(pattern, clarification, content, count=1)
        
        return content
    
    def _optimize_flow(self, content: str) -> str:
        """优化流程描述。"""
        # 添加流程编号
        pattern = r'(Phase \d+:)'
        
        def add_numbering(match):
            return f'### {match.group(1)}'
        
        content = re.sub(pattern, add_numbering, content)
        
        return content


class ReflectionEngine:
    """反思引擎。"""
    
    def reflect(
        self,
        variant_scores: List[Dict[str, Any]],
        original_content: str
    ) -> Tuple[str, List[str]]:
        """分析失败原因，生成改进建议。"""
        
        insights = []
        improvements = []
        
        # 分析失败模式
        for variant in variant_scores:
            if not variant.get('valid', False):
                constraints = variant.get('constraints', [])
                for constraint in constraints:
                    if not constraint['passed']:
                        insights.append(f"约束 '{constraint['constraint']}' 失败: {constraint['message']}")
        
        # 分析低分维度
        for variant in variant_scores:
            scores = variant.get('scores', {})
            for dim, score in scores.items():
                if dim != 'total' and score < 0.6:
                    insights.append(f"维度 '{dim}' 分数较低: {score:.2f}")
        
        # 生成改进建议
        if any('clarity' in insight for insight in insights):
            improvements.append("简化指令表达，拆分长段落")
        
        if any('completeness' in insight for insight in insights):
            improvements.append("补充缺失的关键章节")
        
        if any('size' in insight for insight in insights):
            improvements.append("精简冗余内容，删除重复描述")
        
        # 生成改进版本
        improved_content = self._apply_improvements(original_content, improvements)
        
        return improved_content, improvements
    
    def _apply_improvements(self, content: str, improvements: List[str]) -> str:
        """应用改进建议。"""
        mutation = MutationStrategy(0.2)
        
        for improvement in improvements:
            if '简化' in improvement:
                content = mutation._simplify_section(content)
            elif '补充' in improvement:
                content = mutation._add_example(content)
            elif '精简' in improvement:
                content = self._reduce_redundancy(content)
        
        return content
    
    def _reduce_redundancy(self, content: str) -> str:
        """减少冗余。"""
        lines = content.split('\n')
        
        # 移除空行冗余
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
        
        return '\n'.join(cleaned)


class GEPAOptimizer:
    """GEPA 进化优化器（兼容版本）。"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.gepa_config = config.get('gepa', {})
        
        self.mutation_rate = self.gepa_config.get('mutation_rate', 0.3)
        self.objectives = self.gepa_config.get('pareto_objectives', [
            'accuracy', 'clarity', 'efficiency', 'completeness'
        ])
        self.max_variants_per_gen = self.gepa_config.get('max_variants_per_gen', 5)
        self.reflection_enabled = self.gepa_config.get('reflection_enabled', True)
        
        self.mutation = MutationStrategy(self.mutation_rate)
        self.reflection = ReflectionEngine()
        self.pareto = ParetoSelector()
        
    def optimize(
        self,
        original_content: str,
        test_cases: List[Dict[str, Any]],
        iterations: int = 10,
        evaluator_func: Optional[callable] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """执行进化优化。"""
        
        if GEPA_AVAILABLE:
            return self._optimize_with_gepa(original_content, test_cases, iterations)
        else:
            return self._optimize_fallback(
                original_content,
                test_cases,
                iterations,
                evaluator_func
            )
    
    def _optimize_with_gepa(
        self,
        original: str,
        test_cases: List[Dict[str, Any]],
        iterations: int
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """使用真实 GEPA 优化。"""
        optimizer = RealGEPAOptimizer(
            mutation_rate=self.mutation_rate,
            objectives=self.objectives
        )
        
        history = []
        current_best = original
        
        for i in range(iterations):
            # GEPA 迭代
            variants = optimizer.generate_variants(current_best, self.max_variants_per_gen)
            
            # 评估
            evaluated = []
            for variant in variants:
                # 使用 GEPA 内置评估
                score = optimizer.evaluate(variant, test_cases)
                evaluated.append({
                    'content': variant,
                    'scores': score,
                    'generation': i + 1
                })
            
            # Pareto 选择
            selected = optimizer.pareto_select(evaluated)
            history.extend(selected)
            
            if selected:
                current_best = selected[0]['content']
            
            # 反思
            if self.reflection_enabled:
                improved, insights = self.reflection.reflect(
                    evaluated,
                    current_best
                )
                if insights:
                    print(f"Gen {i+1} reflections: {insights}")
        
        return current_best, history
    
    def _optimize_fallback(
        self,
        original: str,
        test_cases: List[Dict[str, Any]],
        iterations: int,
        evaluator_func: Optional[callable]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """备用优化策略。"""
        
        history = []
        current_best = original
        best_score = 0.0
        
        for i in range(iterations):
            print(f"Generation {i+1}/{iterations}")
            
            # 生成变体
            variants = []
            for j in range(self.max_variants_per_gen):
                variant = self.mutation.mutate(current_best)
                variant = self._add_evolution_marker(variant, i + 1, j + 1)
                variants.append(variant)
            
            # 评估变体
            evaluated = []
            for variant in variants:
                if evaluator_func:
                    scores = evaluator_func(variant, test_cases)
                else:
                    scores = self._default_evaluate(variant)
                
                evaluated.append({
                    'content': variant,
                    'scores': scores,
                    'generation': i + 1
                })
            
            # Pareto 选择
            selected = self.pareto.select_best(evaluated, self.objectives)
            
            if selected:
                # 更新最佳
                best = self.pareto.select_single_best(evaluated, self.objectives)
                if best and best['scores']['total'] > best_score:
                    current_best = best['content']
                    best_score = best['scores']['total']
                
                history.extend(selected)
                
                print(f"  Selected {len(selected)} variants, best score: {best_score:.2f}")
            
            # 反思改进
            if self.reflection_enabled and i > 0:
                improved, insights = self.reflection.reflect(evaluated, current_best)
                if insights:
                    print(f"  Reflections: {insights[:3]}")
        
        return current_best, history
    
    def _default_evaluate(self, variant: str) -> Dict[str, float]:
        """默认评估（简化版）。"""
        from evaluator import QualityScorer
        
        scorer = QualityScorer()
        scores = scorer._score_heuristic(variant)
        scores['total'] = scorer._calculate_total(scores)
        scores['constraint_passed'] = True
        
        return scores
    
    def _add_evolution_marker(
        self,
        content: str,
        generation: int,
        variant_id: int
    ) -> str:
        """添加进化标记。"""
        marker = f"""
<!-- Digimon Evolution: {datetime.now().strftime('%Y-%m-%d')} | generation: {generation} | variant: {variant_id} -->
"""
        
        # 在文件开头添加
        if not content.startswith('<!-- Digimon'):
            return marker + '\n' + content
        else:
            return content
    
    def generate_variants(
        self,
        content: str,
        num_variants: int
    ) -> List[str]:
        """生成变体（供外部调用）。"""
        variants = []
        for i in range(num_variants):
            variant = self.mutation.mutate(content)
            variant = self._add_evolution_marker(variant, 0, i + 1)
            variants.append(variant)
        return variants
    
    def reflect_and_improve(
        self,
        selected_variants: List[Dict[str, Any]],
        current_content: str
    ) -> str:
        """反思并改进。"""
        improved, insights = self.reflection.reflect(selected_variants, current_content)
        return improved


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='GEPA Optimizer')
    parser.add_argument('--content', required=True)
    parser.add_argument('--iterations', type=int, default=10)
    
    args = parser.parse_args()
    
    config = {
        'gepa': {
            'mutation_rate': 0.3,
            'pareto_objectives': ['accuracy', 'clarity', 'efficiency', 'completeness'],
            'reflection_enabled': True,
            'max_variants_per_gen': 5
        }
    }
    
    optimizer = GEPAOptimizer(config)
    best, history = optimizer.optimize(
        args.content,
        [],
        args.iterations
    )
    
    print(f"Best score: {optimizer._default_evaluate(best)['total']:.2f}")
    print(f"Total variants: {len(history)}")