"""
Variant Evaluator Module

评估进化变体质量，检查约束条件。
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import dspy
    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False


class ConstraintChecker:
    """约束条件检查器。"""
    
    def __init__(self, constraints_config: Dict[str, Any]):
        self.constraints = constraints_config
        
    def check_all(self, variant: str, original: str) -> List[Dict[str, Any]]:
        """检查所有约束条件。"""
        results = []
        
        # 大小约束
        results.append(self._check_size(variant))
        
        # 结构保留
        results.append(self._check_structure(variant, original))
        
        # 语义一致性
        results.append(self._check_semantic(variant, original))
        
        # 破坏性检查
        results.append(self._check_destructive(variant, original))
        
        # 关键内容保留
        results.append(self._check_critical_content(variant, original))
        
        return results
    
    def _check_size(self, variant: str) -> Dict[str, Any]:
        """检查大小约束。"""
        size_kb = len(variant) / 1024
        max_kb = self.constraints.get('max_size_kb', 15)
        
        return {
            'constraint': 'max_size_kb',
            'passed': size_kb <= max_kb,
            'value': size_kb,
            'limit': max_kb,
            'message': f'Size {size_kb:.2f}KB vs limit {max_kb}KB'
        }
    
    def _check_structure(self, variant: str, original: str) -> Dict[str, Any]:
        """检查结构保留。"""
        orig_sections = set(self._extract_sections(original))
        var_sections = set(self._extract_sections(variant))
        
        missing = orig_sections - var_sections
        
        return {
            'constraint': 'preserve_structure',
            'passed': len(missing) == 0,
            'original_sections': len(orig_sections),
            'variant_sections': len(var_sections),
            'missing_sections': list(missing),
            'message': f'{len(missing)} sections removed'
        }
    
    def _check_semantic(self, variant: str, original: str) -> Dict[str, Any]:
        """检查语义一致性。"""
        keywords = ['触发条件', '工作流程', '执行', '约束', '注意', '示例']
        
        orig_keywords = sum(1 for kw in keywords if kw in original)
        var_keywords = sum(1 for kw in keywords if kw in variant)
        
        ratio = var_keywords / orig_keywords if orig_keywords > 0 else 0
        
        return {
            'constraint': 'semantic_check',
            'passed': ratio >= 0.8,
            'original_keywords': orig_keywords,
            'variant_keywords': var_keywords,
            'preservation_ratio': ratio,
            'message': f'Keyword preservation {ratio:.2%}'
        }
    
    def _check_destructive(self, variant: str, original: str) -> Dict[str, Any]:
        """检查破坏性变更。"""
        destructive_patterns = [
            r'删除\s*全部',
            r'移除\s*关键',
            r'忽略\s*约束',
            r'跳过\s*检查'
        ]
        
        found_destructive = []
        for pattern in destructive_patterns:
            if re.search(pattern, variant):
                found_destructive.append(pattern)
        
        return {
            'constraint': 'destructive_check',
            'passed': len(found_destructive) == 0,
            'found_patterns': found_destructive,
            'message': f'{len(found_destructive)} destructive patterns found'
        }
    
    def _check_critical_content(self, variant: str, original: str) -> Dict[str, Any]:
        """检查关键内容保留。"""
        critical_sections = ['触发条件', '约束规则', '注意事项']
        
        preserved = []
        lost = []
        
        for section in critical_sections:
            if section in original:
                if section in variant:
                    preserved.append(section)
                else:
                    lost.append(section)
        
        return {
            'constraint': 'critical_content',
            'passed': len(lost) == 0,
            'preserved': preserved,
            'lost': lost,
            'message': f'{len(preserved)} preserved, {len(lost)} lost'
        }
    
    def _extract_sections(self, content: str) -> List[str]:
        """提取章节标题。"""
        sections = []
        for line in content.split('\n'):
            if line.startswith('## ') or line.startswith('### '):
                sections.append(line.strip())
        return sections


class QualityScorer:
    """变体质量评分器。"""
    
    WEIGHTS = {
        'accuracy': 0.3,
        'clarity': 0.25,
        'efficiency': 0.2,
        'completeness': 0.25
    }
    
    def score_variant(
        self,
        variant: str,
        test_cases: List[Dict[str, Any]],
        constraints_result: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """评分变体质量。"""
        
        # 约束不通过则返回低分
        if not all(r['passed'] for r in constraints_result):
            return {
                'accuracy': 0.0,
                'clarity': 0.0,
                'efficiency': 0.0,
                'completeness': 0.0,
                'total': 0.0,
                'constraint_passed': False
            }
        
        scores = {}
        
        if DSPY_AVAILABLE:
            scores = self._score_with_dspy(variant, test_cases)
        else:
            scores = self._score_heuristic(variant)
        
        scores['total'] = self._calculate_total(scores)
        scores['constraint_passed'] = True
        
        return scores
    
    def _score_with_dspy(self, variant: str, test_cases: List[Dict[str, Any]]) -> Dict[str, float]:
        """使用 DSPy 评分。"""
        class QualitySignature(dspy.Signature):
            variant: str = dspy.InputField(desc="Variant content")
            test_cases: str = dspy.InputField(desc="JSON test cases")
            scores: str = dspy.OutputField(desc="JSON scores: accuracy, clarity, efficiency, completeness")
        
        scorer = dspy.ChainOfThought(QualitySignature)
        result = scorer(
            variant=variant,
            test_cases=json.dumps(test_cases)
        )
        
        try:
            return json.loads(result.scores)
        except json.JSONDecodeError:
            return self._score_heuristic(variant)
    
    def _score_heuristic(self, variant: str) -> Dict[str, float]:
        """启发式评分。"""
        return {
            'accuracy': 0.75,
            'clarity': self._score_clarity(variant),
            'efficiency': self._score_efficiency(variant),
            'completeness': self._score_completeness(variant)
        }
    
    def _score_clarity(self, variant: str) -> float:
        """评分清晰度。"""
        lines = variant.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        if not non_empty_lines:
            return 0.0
        
        avg_length = sum(len(l) for l in non_empty_lines) / len(non_empty_lines)
        
        if avg_length < 50:
            return 0.9
        elif avg_length < 80:
            return 0.75
        else:
            return 0.6
    
    def _score_efficiency(self, variant: str) -> float:
        """评分效率。"""
        # 检查是否有冗余内容
        lines = variant.split('\n')
        unique_lines = len(set(l.strip() for l in lines if l.strip()))
        total_lines = len([l for l in lines if l.strip()])
        
        if total_lines == 0:
            return 0.0
        
        redundancy_ratio = unique_lines / total_lines
        
        return min(redundancy_ratio, 1.0) * 0.9 + 0.1
    
    def _score_completeness(self, variant: str) -> float:
        """评分完整性。"""
        required_sections = ['触发条件', '工作流程', '约束']
        optional_sections = ['示例', '注意事项', '最佳实践']
        
        required_found = sum(1 for s in required_sections if s in variant)
        optional_found = sum(1 for s in optional_sections if s in variant)
        
        required_score = required_found / len(required_sections)
        optional_score = optional_found / len(optional_sections) * 0.3
        
        return required_score * 0.7 + optional_score + 0.3
    
    def _calculate_total(self, scores: Dict[str, float]) -> float:
        """计算总分。"""
        total = 0.0
        for key, weight in self.WEIGHTS.items():
            total += scores.get(key, 0.0) * weight
        return total


class ParetoSelector:
    """Pareto 前沿选择器。"""
    
    def select_best(
        self,
        variants: List[Dict[str, Any]],
        objectives: List[str]
    ) -> List[Dict[str, Any]]:
        """选择 Pareto 最优变体。"""
        
        if not variants:
            return []
        
        # 计算每个变体的目标值
        scored_variants = []
        for variant in variants:
            scores = variant.get('scores', {})
            obj_values = [scores.get(obj, 0.0) for obj in objectives]
            scored_variants.append({
                'variant': variant,
                'objectives': obj_values
            })
        
        # Pareto 前沿选择
        pareto_front = []
        
        for i, candidate in enumerate(scored_variants):
            is_dominated = False
            
            for j, other in enumerate(scored_variants):
                if i == j:
                    continue
                
                # 检查是否被支配
                dominated = all(
                    other['objectives'][k] >= candidate['objectives'][k]
                    for k in range(len(objectives))
                )
                
                if dominated:
                    is_dominated = True
                    break
            
            if not is_dominated:
                pareto_front.append(candidate['variant'])
        
        return pareto_front
    
    def select_single_best(
        self,
        variants: List[Dict[str, Any]],
        objectives: List[str]
    ) -> Optional[Dict[str, Any]]:
        """选择单一最优变体。"""
        pareto_front = self.select_best(variants, objectives)
        
        if not pareto_front:
            return None
        
        # 从 Pareto 前沿中选择总分最高的
        best = max(
            pareto_front,
            key=lambda v: v.get('scores', {}).get('total', 0.0)
        )
        
        return best


def evaluate_variants(
    variants: List[str],
    original: str,
    test_cases: List[Dict[str, Any]],
    constraints_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """评估多个变体。"""
    
    checker = ConstraintChecker(constraints_config)
    scorer = QualityScorer()
    
    results = []
    
    for i, variant in enumerate(variants):
        constraints_result = checker.check_all(variant, original)
        scores = scorer.score_variant(variant, test_cases, constraints_result)
        
        results.append({
            'id': f'variant-{i+1:03d}',
            'content': variant,
            'constraints': constraints_result,
            'scores': scores,
            'valid': scores['constraint_passed']
        })
    
    return results


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate variants')
    parser.add_argument('--variant', required=True)
    parser.add_argument('--original', required=True)
    
    args = parser.parse_args()
    
    constraints = {
        'max_size_kb': 15,
        'preserve_structure': True,
        'semantic_check': True
    }
    
    checker = ConstraintChecker(constraints)
    results = checker.check_all(args.variant, args.original)
    
    print(json.dumps(results, indent=2))