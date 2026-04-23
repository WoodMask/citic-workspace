# Constraints Definition

Digimon 约束规则详细定义。

## 约束分类

### 硬约束 (Hard Constraints)

必须通过，否则变体被拒绝。

| 约束ID | 名称 | 规则 | 检查方法 |
|--------|------|------|----------|
| `HC-001` | 文件大小 | ≤15KB | `len(content) / 1024 <= 15` |
| `HC-002` | 关键章节 | 不可删除 | `required_sections in variant` |
| `HC-003` | 语义一致 | ≥80%关键词保留 | `keyword_ratio >= 0.8` |
| `HC-004` | 破坏性检查 | 无破坏性模式 | `no destructive patterns` |

### 软约束 (Soft Constraints)

影响评分，但不直接拒绝。

| 约束ID | 名称 | 规则 | 影响 |
|--------|------|------|------|
| `SC-001` | 清晰度 | 平均行长≤80 | clarity_score -10% |
| `SC-002` | 完整性 | 包含示例章节 | completeness_score -5% |
| `SC-003` | 效率 | 独特行≥90% | efficiency_score -10% |

## 约束检查实现

### HC-001: 文件大小

```python
def check_size(variant: str, max_kb: float = 15.0) -> dict:
    size_kb = len(variant) / 1024
    return {
        'constraint': 'HC-001',
        'passed': size_kb <= max_kb,
        'value': size_kb,
        'limit': max_kb
    }
```

### HC-002: 关键章节

```python
REQUIRED_SECTIONS = ['触发条件', '工作流程', '约束']

def check_required_sections(variant: str, original: str) -> dict:
    orig_sections = extract_sections(original)
    var_sections = extract_sections(variant)
    
    required_in_orig = [s for s in orig_sections if any(r in s for r in REQUIRED_SECTIONS)]
    required_in_var = [s for s in var_sections if any(r in s for r in REQUIRED_SECTIONS)]
    
    missing = set(required_in_orig) - set(required_in_var)
    
    return {
        'constraint': 'HC-002',
        'passed': len(missing) == 0,
        'missing': list(missing)
    }
```

### HC-003: 语义一致

```python
KEYWORDS = ['触发条件', '工作流程', '执行', '约束', '注意事项', '示例']

def check_semantic(variant: str, original: str) -> dict:
    orig_count = sum(1 for kw in KEYWORDS if kw in original)
    var_count = sum(1 for kw in KEYWORDS if kw in variant)
    
    ratio = var_count / orig_count if orig_count > 0 else 0
    
    return {
        'constraint': 'HC-003',
        'passed': ratio >= 0.8,
        'ratio': ratio
    }
```

### HC-004: 破坏性检查

```python
DESTRUCTIVE_PATTERNS = [
    r'删除\s*全部',
    r'移除\s*关键',
    r'忽略\s*约束',
    r'跳过\s*检查',
    r'绕过\s*验证'
]

def check_destructive(variant: str) -> dict:
    found = []
    for pattern in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, variant):
            found.append(pattern)
    
    return {
        'constraint': 'HC-004',
        'passed': len(found) == 0,
        'found_patterns': found
    }
```

## 约束配置

在 `config.json` 中配置：

```json
{
  "evolution": {
    "constraints": {
      "max_size_kb": 15,
      "required_sections": ["触发条件", "工作流程", "约束"],
      "semantic_threshold": 0.8,
      "destructive_patterns": ["删除全部", "移除关键", "忽略约束"],
      "backup_before_apply": true
    }
  }
}
```

## 约束优先级

约束按优先级检查，高优先级失败立即终止：

```
HC-001 (文件大小) → HC-002 (关键章节) → HC-003 (语义) → HC-004 (破坏性)
        ↓                   ↓                 ↓              ↓
     立即拒绝            立即拒绝          立即拒绝        立即拒绝
```

## 约束报告格式

```json
{
  "constraint_report": {
    "variant_id": "variant-003",
    "total_constraints": 8,
    "passed": 7,
    "failed": 1,
    "details": [
      {
        "constraint": "HC-001",
        "passed": true,
        "value": 12.5,
        "limit": 15
      },
      {
        "constraint": "HC-002",
        "passed": false,
        "missing": ["注意事项"]
      }
    ]
  }
}
```

## 自定义约束

可添加自定义约束：

```python
# 自定义约束示例
def check_custom(variant: str) -> dict:
    # 检查是否包含特定格式
    has_marker = '<!-- Digimon Evolution' in variant
    
    return {
        'constraint': 'CUSTOM-001',
        'passed': has_marker,
        'description': 'Must contain evolution marker'
    }
```

在 config.json 中注册：

```json
{
  "evolution": {
    "constraints": {
      "custom_constraints": [
        {
          "id": "CUSTOM-001",
          "description": "Evolution marker required",
          "enabled": true
        }
      ]
    }
  }
}
```

## 约束放宽策略

在某些场景可放宽约束：

| 场景 | 放宽约束 | 新值 |
|------|----------|------|
| **大型技能** | max_size_kb | 20KB |
| **简单技能** | required_sections | 仅 "触发条件" |
| **实验阶段** | semantic_threshold | 0.7 |

配置放宽：

```json
{
  "evolution": {
    "constraint_relaxation": {
      "enabled": false,
      "rules": {
        "large_skill": {"max_size_kb": 20},
        "simple_skill": {"required_sections": ["触发条件"]}
      }
    }
  }
}
```