# Skill: digimon

基于 DSPy + GEPA (Genetic-Pareto Prompt Evolution) 的技能自进化系统，优化 opencode 的 Skills、Prompts、Tools。

## 触发条件

当用户请求以下内容时触发此技能：
- "digimon 进化 XX skill"
- "digimon 运行"
- "技能进化"
- "优化 XX skill"
- "自进化"

## 进化目标

| 目标类型 | 文件路径 | 状态 |
|----------|----------|------|
| **Skills** | SKILL.md | ✅ 已支持 |
| **Prompts** | 系统提示段落 | 🔲 Phase 2 |
| **Tools** | 工具描述 | 🔲 Phase 2 |
| **Python代码** | scripts/*.py | 🔲 Phase 3 |

## 工作流程

```
┌──────────────────────────────────────────────────────────────┐
│                    DIGIMON 进化流程                            │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  用户触发: "digimon 进化 open-source-tech-report"             │
│              │                                               │
│              ▼                                               │
│  ┌───────────────────────────────────────┐                   │
│  │ 1. 分析目标 skill                       │                   │
│  │    - 读取 SKILL.md 结构                 │                   │
│  │    - 提取指令、示例、流程                │                   │
│  │    - 识别可优化部分                      │                   │
│  └───────────────────────────────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│  ┌───────────────────────────────────────┐                   │
│  │ 2. 生成评估数据集                       │                   │
│  │    来源选择:                            │                   │
│  │    - sessiondb: 真实会话历史            │                   │
│  │    - synthetic: 合成测试用例            │                   │
│  │    - traces: 执行轨迹分析               │                   │
│  └───────────────────────────────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│  ┌───────────────────────────────────────┐                   │
│  │ 3. GEPA 进化优化                        │                   │
│  │    ┌────────────────────────────────┐ │                   │
│  │    │ 迭代 N 次:                      │ │                   │
│  │    │  a. 变体生成 (mutation)         │ │                   │
│  │    │  b. 执行评估                    │ │                   │
│  │    │  c. 反思改进                    │ │                   │
│  │    │  d. Pareto 选择                 │ │                   │
│  │    └────────────────────────────────┘ │                   │
│  └───────────────────────────────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│  ┌───────────────────────────────────────┐                   │
│  │ 4. 约束检查                             │                   │
│  │    ✅ 测试套件通过                       │                   │
│  │    ✅ 大小限制 (≤15KB)                  │                   │
│  │    ✅ 语义一致性检查                     │                   │
│  │    ✅ 无破坏性变更                       │                   │
│  └───────────────────────────────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│  ┌───────────────────────────────────────┐                   │
│  │ 5. 应用改进                             │                   │
│  │    - 备份原版本 → memory/variants/      │                   │
│  │    - 应用最优变体                       │                   │
│  │    - 创建 PR (可选)                     │                   │
│  │    - 记录进化历史                       │                   │
│  └───────────────────────────────┬───────┘                   │
│                                  │                           │
│                                  ▼                           │
│                         进化报告 → 用户                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## 执行命令

```bash
# 基本用法
python .opencode/skills/digimon/scripts/evolve.py --skill <skill_name>

# 指定迭代次数
python .opencode/skills/digimon/scripts/evolve.py --skill <skill_name> --iterations 10

# 指定评估数据来源
python .opencode/skills/digimon/scripts/evolve.py --skill <skill_name> --eval-source sessiondb

# 合成数据
python .opencode/skills/digimon/scripts/evolve.py --skill <skill_name> --eval-source synthetic

# 指定目标类型
python .opencode/skills/digimon/scripts/evolve.py --skill <skill_name> --target skill
python .opencode/skills/digimon/scripts/evolve.py --skill <skill_name> --target prompt
python .opencode/skills/digimon/scripts/evolve.py --skill <skill_name> --target tool
```

## 配置文件

配置位于 `config.json`，可调整：
- 进化迭代次数
- 评估数据来源
- 约束规则
- GEPA 参数
- LLM 模型设置

## 约束规则

每次进化的变体必须通过以下约束：

| 约束 | 规则 | 检查方法 |
|------|------|----------|
| **测试套件** | 100% 通过 | pytest tests/ -q |
| **大小限制** | Skills ≤15KB, 工具描述 ≤500字符 | 文件大小检查 |
| **缓存兼容** | 无 mid-conversation 变更 | 时间戳检查 |
| **语义保留** | 不偏离原始目的 | DSPy semantic check |
| **破坏性检查** | 无删除关键章节 | diff 分析 |

## 进化标记格式

进化后的 skill 文件会添加进化标记：

```markdown
<!-- Digimon Evolution: 2026-04-23 | generation: 3 | score: 0.92 | source: sessiondb -->

## [Digimon] 进化记录 (2026-04-23)

**原始版本**: v1.0 (score: 0.65)
**进化变体**: variant-003
**迭代次数**: 10
**改进点**:
- 简化触发条件描述
- 增加执行流程图
- 补充约束规则章节
- 优化指令表达清晰度

**评估结果**: 通过全部约束检查
**Pareto优化**: accuracy↑15%, clarity↑20%
```

## 与 self-improving-agent 协同

| Skill | 技术栈 | 职责 | 触发时机 |
|-------|--------|------|----------|
| **self-improving-agent** | 多记忆架构 + Hooks | 会话经验收集、模式提取 | Hooks 自动触发 |
| **digimon** | DSPy + GEPA | 结构化进化、变体优化 | 手动/阈值触发 |

协同流程：
```
self-improving-agent 收集失败经验 → memory/episodic/
                    ↓
触发 digimon 进化分析
                    ↓
从 memory/ 读取经验作为评估数据
                    ↓
生成针对性改进变体
                    ↓
应用优化版本 → 记录进化历史
```

## 技术依赖

```bash
pip install dspy gepa
```

或使用 pyproject.toml:
```toml
[project.dependencies]
dspy = ">=2.5"
gepa = ">=0.1.0"
```

## 目录结构

```
.opencode/skills/digimon/
├── SKILL.md                 # Skill 定义 + 进化工作流
├── scripts/
│   ├── evolve.py            # 进化核心脚本 (统一入口)
│   ├── trace_analyzer.py    # 执行轨迹分析器
│   ├── evaluator.py         # 变体评估器
│   ├── dataset_generator.py # 评估数据集生成
│   └── gepa_optimizer.py    # GEPA 优化器集成
├── memory/
│   ├── traces/              # 执行轨迹存储
│   ├── evaluations/         # 评估数据集 JSON
│   ├── variants/            # 进化变体历史
│   └── semantic/            # 语义模式库
├── config.json              # GEPA 配置 + LLM 设置
└── reference/
    ├── gepa_guide.md        # GEPA 使用指南
    ├── evolution_patterns.md # 进化模式参考
    └── constraints.md       # 约束规则定义
```

## 最佳实践

### DO

- ✅ 从真实会话历史生成评估数据 (sessiondb)
- ✅ 设置合理的迭代次数 (5-15)
- ✅ 应用改进前备份原版本
- ✅ 记录进化历史和改进点
- ✅ 用户确认后再应用重大变更
- ✅ 定期清理旧变体历史

### DON'T

- ❌ 过度进化导致内容膨胀
- ❌ 忽略约束检查
- ❌ 直接应用未经测试的变体
- ❌ 进化后删除关键章节
- ❌ 创建矛盾或重复的指令

## 调用示例

### Python 脚本调用

```python
from scripts.evolve import SkillEvolver

evolver = SkillEvolver(
    skill_name="open-source-tech-report",
    iterations=10,
    eval_source="sessiondb"
)

result = evolver.evolve()
print(f"进化完成: score {result['score']}, improvements {result['improvements']}")
```

### 作为 Skill 调用

在对话中直接说：
- "digimon 进化 open-source-tech-report"
- "运行 digimon，目标 skill 是 send-citic-mail"

## 注意事项

1. **DSPy + GEPA 需要 LLM API**: 配置 config.json 中的 LLM 设置
2. **进化成本**: 每次 $2-10，取决于迭代次数和模型选择
3. **sessiondb 数据**: 需要有足够的历史会话数据才能有效进化
4. **首次进化**: 建议使用 synthetic 数据生成初始评估集
5. **约束优先**: 约束检查失败则不应用变体

## 相关参考

- [GEPA: Genetic-Pareto Prompt Evolution](https://github.com/gepa-ai/gepa)
- [DSPy: Declarative Self-improving Language Programs](https://github.com/stanfordnlp/dspy)
- [Hermes Agent Self-Evolution](https://github.com/NousResearch/hermes-agent-self-evolution)