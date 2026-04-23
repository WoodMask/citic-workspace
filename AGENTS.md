# citic-workspace

中信工作空间项目，包含工作看板管理、邮件发送、技术评估报告生成等功能。

## 项目概述

本项目为中信信用卡中心工作辅助工具集合，主要功能包括：

- **工作看板管理**：管理模型推理服务工作项，支持任务增删改查、进度报告、日期提醒
- **邮件发送**：发送附件和正文到公司邮箱
- **技术评估报告**：生成开源技术引入风险与技术评估报告（.docx格式）

## 目录结构

```
citic-workspace/
├── .opencode/
│   ├── skills/                 # 自定义技能目录
│   │   ├── citic-workboard/    # 工作看板管理技能
│   │   ├── send-citic-mail/    # 邮件发送技能
│   │   ├── open-source-tech-report/  # 技术评估报告技能
│   │   ├── useskills/          # Skill组合加载器
│   │   └── serpapi-search/     # 搜索技能
│   └── useskills.json          # Skill组合配置
├── workboard.py                # 看板HTML生成脚本
├── 工作看板.html               # 生成的看板页面
├── 模型推理服务.xlsx           # 工作项数据源
└── report-template/            # 报告模板目录
```

## 技能系统

| 技能名称 | 功能描述 |
|----------|----------|
| citic-workboard | 工作看板管理，支持任务增删改查、进度报告、日期提醒 |
| send-citic-mail | 发送邮件到公司邮箱，支持附件和正文 |
| open-source-tech-report | 生成开源技术引入风险与技术评估报告 |
| useskills | Skill组合加载器，支持多模式切换 |
| serpapi-search | 网络搜索，用于获取技术信息 |

### 模式配置

项目支持以下工作模式：

| 模式 | 包含技能 | 适用场景 |
|------|----------|----------|
| default | serpapi-search, tavily-search, xlsx, gh-cli | 日常工作 |
| report | open-source-tech-report, xlsx, serpapi-search | 报告生成 |
| coding | serpapi-search, tavily-search, gh-cli, skill-creator | 编码开发 |
| agent | proactive-agent, self-improving-agent, remembering-conversations | Agent增强 |

切换模式命令：
- "切换到报告模式"
- "使用coding模式"

## 技能优先级

使用技能时遵循以下优先级顺序：

| 优先级 | 来源 | 示例 |
|--------|------|------|
| **1（最高）** | 项目技能 `.opencode/skills/` | citic-workboard, send-citic-mail |
| **2** | 全局技能 `~/.agents/skills/` | tavily-search, xlsx |
| **3（最低）** | 系统内置 | 基础工具 |

**执行原则**：
- 用户请求功能时，优先查找项目技能目录
- 项目技能可覆盖全局同名技能
- 未找到时才使用全局或内置技能
- 通过 useskills.json 的 `projectSkills` 字段定义项目专属技能列表

**当前项目专属技能**：
```json
"projectSkills": ["useskills", "serpapi-search", "open-source-tech-report", "send-citic-mail"]
```

## 开发规范

### Git提交规范

```
feat: 新功能
fix: 修复问题
chore: 杂项（数据更新、配置调整）
docs: 文档更新
refactor: 重构
```

### Python代码规范

- 使用UTF-8编码
- 函数命名：snake_case
- 类命名：PascalCase
- 注释使用中文

## 常用命令

### 刷新工作看板

```bash
python workboard.py
```

### 更新任务状态

```python
# 使用excel_manager脚本
from excel_manager import update_task_status_by_id
update_task_status_by_id('039', '进行中')
```

### 发送邮件

```bash
python .opencode/skills/send-citic-mail/send_email.py -a "附件路径" -s "邮件标题"
```

### 生成技术评估报告

```bash
python .opencode/skills/open-source-tech-report/scripts/generate_report.py
```

## 配置说明

### useskills.json

位置：`.opencode/useskills.json`

配置字段：
- `activeProfile`: 当前激活模式
- `profiles`: 模式配置集合
- `autoLoad`: 是否自动加载（默认true）

### 邮件配置

位置：`.opencode/skills/send-citic-mail/config.json`

配置项：
- `sender`: 发件人邮箱
- `receiver`: 收件人邮箱（公司邮箱）
- `auth_code`: SMTP授权码
- `smtp_server`: SMTP服务器
- `smtp_port`: SMTP端口

## 数据文件

### 模型推理服务.xlsx

工作看板数据源，Excel结构：

| 列 | 字段 |
|---|------|
| A | 任务编号 |
| B | 任务 |
| C | 任务状态 |
| D | 开始日期 |
| E | 完成日期 |
| F | 交付物 |
| G | 备注 |

任务状态：已完成 / 进行中 / 未启动

## 注意事项

1. **Excel文件锁定**：修改Excel前请确保文件未被其他程序占用
2. **任务编号格式**：三位数字格式（001, 002...），支持 39/039/#39 等输入
3. **邮件附件大小**：QQ邮箱单邮件附件总大小限制50MB
4. **看板筛选**：默认只显示"进行中"状态任务，可通过多选框筛选

## 维护者

Mask