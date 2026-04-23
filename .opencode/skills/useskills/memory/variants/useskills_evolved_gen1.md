<!-- Digimon Evolution: 2026-04-23 | gen:1 -->
---
name: useskills
description: |
  Skill组合加载器。在会话开始时自动触发，读取项目配置.opencode/useskills.json，
  按定义顺序优先加载指定的skill组合。支持多模式切换（如default/report/coding）。
  当用户提到"切换模式"、"使用xx模式"或启动新会话时自动使用。
---

# UseSkills - Skill组合加载器

根据项目配置自动加载优先skill组合，形成工作流。

## 配置文件

项目级配置位置：`.opencode/useskills.json`

### 配置格式

```json
{
  "version": 1,
  "profiles": {
    "default": {
      "skills": ["tavily-search", "xlsx", "gh-cli"],
      "description": "默认配置"
    },
    "report": {
      "skills": ["research", "xlsx", "frontend-design"],
      "description": "报告模式"
    }
  },
  "activeProfile": "default",
  "autoLoad": true
}
```

## 工作流程

1. **自动加载**：会话开始时，读取`activeProfile`指定的配置
2. **顺序加载**：按`skills`数组顺序依次调用skill工具
3. **模式切换**：用户说"切换到xx模式"时，更新activeProfile并重新加载

## 命令识别

| 用户输入 | 行为 |
|----------|------|
| `切换到报告模式` / `使用report模式` | 加载profiles.report中的skills |
| `切换模式 coding` | 加载profiles.coding中的skills |
| `列出配置` / `显示所有模式` | 输出profiles列表 |
| `当前配置` / `当前模式` | 显示activeProfile名称和skills列表 |

## 配置字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| version | number | 是 | 配置版本号 |
| profiles | object | 是 | 模式配置集合 |
| activeProfile | string | 是 | 当前激活的模式名 |
| autoLoad | boolean | 否 | 是否自动加载（默认true） |

## 执行逻辑

当触发此skill时：

1. 检查`.opencode/useskills.json`是否存在
2. 若不存在，提示用户创建配置文件
3. 若存在，读取配置并获取`activeProfile`
4. 按顺序执行：`skill({ name: "skill-name-1" })` → `skill({ name: "skill-name-2" })` ...
5. 每加载一个skill，简要说明其用途

## 示例输出

```
已加载 [default] 模式：
✓ tavily-search - 网络搜索
✓ xlsx - 表格处理
✓ gh-cli - GitHub操作

共加载3个skill，可开始使用。
```

## 内置模式说明

| 模式 | 包含Skills | 适用场景 |
|------|-----------|----------|
| default | tavily-search, xlsx, gh-cli | 日常开发工作 |
| report | research, xlsx, frontend-design | 撰写报告/文档 |
| coding | tavily-search, gh-cli, skill-creator | 编码/创建新skill |
| agent | proactive-agent, self-improving-agent, remembering-conversations | Agent增强场景 |