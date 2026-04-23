# GEPA Guide

GEPA (Genetic-Pareto Prompt Evolution) 使用指南。

## 概述

GEPA 是一种反思性进化算法，用于优化 LLM 提示和技能文件。它结合了：

- **遗传变异 (Genetic Mutation)**: 随机生成变体
- **Pareto 选择**: 多目标优化，选择非支配解
- **反思改进 (Reflection)**: 分析失败原因，针对性改进

## 核心概念

### 1. 变体生成 (Mutation)

从原始内容生成候选变体，变异操作包括：

| 操作类型 | 说明 | 效果 |
|----------|------|------|
| `simplify_section` | 简化过长段落 | 提高清晰度 |
| `expand_instruction` | 扩展指令说明 | 提高完整性 |
| `add_example` | 添加使用示例 | 提高实用性 |
| `clarify_constraint` | 澄清约束说明 | 提高准确性 |
| `optimize_flow` | 优化流程描述 | 提高效率 |

### 2. 多目标优化 (Pareto)

同时优化多个维度：

| 目标 | 权重 | 说明 |
|------|------|------|
| `accuracy` | 30% | 执行正确率 |
| `clarity` | 25% | 指令清晰度 |
| `efficiency` | 20% | 执行效率 |
| `completeness` | 25% | 内容完整性 |

**Pareto 前沿**: 不被其他变体在所有目标上超越的变体集合。

### 3. 反思改进 (Reflection)

分析评估结果，识别失败原因：

```python
# 反思流程
for variant in failed_variants:
    analyze_constraint_failures(variant)
    analyze_low_score_dimensions(variant)
    generate_targeted_improvements()
    apply_improvements_to_next_generation()
```

## 使用方式

### 基本用法

```python
from gepa_optimizer import GEPAOptimizer

config = {
    'gepa': {
        'mutation_rate': 0.3,
        'pareto_objectives': ['accuracy', 'clarity', 'efficiency', 'completeness'],
        'reflection_enabled': True,
        'max_variants_per_gen': 5
    }
}

optimizer = GEPAOptimizer(config)

best_content, history = optimizer.optimize(
    original_content,
    test_cases,
    iterations=10
)
```

### 参数调整

| 参数 | 默认值 | 建议范围 |
|------|--------|----------|
| `mutation_rate` | 0.3 | 0.1 - 0.5 |
| `iterations` | 10 | 5 - 20 |
| `max_variants_per_gen` | 5 | 3 - 10 |
| `reflection_enabled` | True | True/False |

## 进化迭代流程

```
Generation 1:
├── 生成 5 个变体
├── 评估每个变体
├── Pareto 选择最优
└── 反思改进

Generation 2:
├── 从最优变体生成新变体
├── 评估
├── Pareto 选择
└── 反思

... (重复 N 次)

最终选择 Pareto 前沿最佳变体
```

## 与 DSPy 集成

DSPy 提供声明式提示编程框架，与 GEPA 结合：

```python
import dspy
from gepa_optimizer import GEPAOptimizer

# 定义 DSPy 签名
class SkillSignature(dspy.Signature):
    skill_content: str = dspy.InputField()
    evaluation_result: str = dspy.OutputField()

# 使用 DSPy 评估
evaluator = dspy.ChainOfThought(SkillSignature)

# GEPA 进化
optimizer = GEPAOptimizer(config)
optimizer.optimize(content, test_cases, iterations=10)
```

## 最佳实践

### DO

- ✅ 从真实数据生成评估集
- ✅ 启用反思功能
- ✅ 设置合理的迭代次数 (10-15)
- ✅ 使用 Pareto 多目标选择
- ✅ 添加约束检查作为硬约束

### DON'T

- ❌ 过高变异率 (>0.5)
- ❌ 过少迭代 (<5)
- ❌ 单一目标优化
- ❌ 忽略约束检查
- ❌ 禁用反思功能

## 输出格式

进化后的内容包含标记：

```markdown
<!-- Digimon Evolution: 2026-04-23 | generation: 3 | score: 0.92 -->

## [Digimon] 进化记录

**原始版本**: v1.0
**进化变体**: variant-003
**改进点**: ...
```

## 参考文献

- [GEPA GitHub](https://github.com/gepa-ai/gepa)
- [DSPy GitHub](https://github.com/stanfordnlp/dspy)
- [Hermes Agent Self-Evolution](https://github.com/NousResearch/hermes-agent-self-evolution)
- ICLR 2026 Oral Paper (GEPA)