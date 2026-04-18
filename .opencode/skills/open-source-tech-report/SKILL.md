# Skill: open-source-tech-report

根据卡中心开源技术引入风险与技术评估报告模板，生成指定开源软件/技术的评估报告文档（.docx格式）。

## 触发条件

当用户请求生成以下类型报告时触发此技能：
- "生成XX的评估报告"
- "XX技术评估报告"
- "XX引入风险报告"
- "开源软件XX评估"

## 必要信息收集

生成报告前，需确认以下信息。缺少时应主动询问用户：

### 基本信息（必须）

| 字段 | 说明 | 示例 |
|------|------|------|
| software_name | 软件/技术名称 | GLM-5.1、Doris、Redis |
| version | 版本号 | 最新版、2.0.10.0 |
| release_date | 发布日期 | 2026-04-18 |
| department | 部门 | 信用卡中心信息技术部 |
| domain | 领域 | 系统级平台域、数据平台工具域 |
| project | 项目组/系统名称 | AI原生应用开发平台 |
| rating | 系统评级 | A、B、C |
| author | 作者姓名 | 吴思楠 |
| reviewer | 审核人姓名 | 陈远川 |

### 技术信息（必须）

| 字段 | 说明 | 示例 |
|------|------|------|
| license | 开源协议 | Apache-2.0、MIT、GPL |
| developer | 开发者/团队 | 智谱AI、Apache社区 |
| github_url | 代码仓库链接 | https://github.com/THUDM/GLM |
| first_release | 第一版发布时间 | 2023-10 |
| last_update | 最后更新时间 | 2026-04 |
| stars | GitHub Star数 | 3500+ |
| commits | Commit次数 | 数千次 |
| contributors | 代码贡献者人数 | 50+ |

### 业务信息（必须）

| 字段 | 说明 | 示例 |
|------|------|------|
| necessity | 引入必要性/用途描述 | 多场景综合使用，长程任务处理 |
| usage_scenarios | 使用场景列表 | Agentic Coding、通用对话、文档生成 |
| comparison | 类似软件对比 | 对比GPT-4o、Claude、DeepSeek |
| service_provider | 服务供应商 | 智谱AI官方API服务 |
| supply_chain_risk | 供应链风险评估 | 较低/中等/较高，及原因 |
| is_initial | 是否初次引入 | True/False |
| usage_plan | 使用计划 | 2026年引入，支撑多场景业务 |

### 可选信息

| 字段 | 说明 |
|------|------|
| vulnerabilities | 近期安全漏洞（如有） |
| upgrade_compatibility | 升级兼容性（仅升级情况） |
| upgrade_test_plan | 升级测试方案（仅升级情况） |

## 报告结构

生成的评估报告包含以下章节：

### 1. 开源软件引入评估

- **1.1 开源软件名称和版本**：填写软件名称和版本号表格
- **1.2 开源软件许可协议**：填写协议类型、注意事项、链接表格
- **1.3 引入必要性评估**：描述引入原因、核心特性、解决的业务问题
- **1.4 类似开源软件对比**：列举同类软件并对比优劣
- **1.5 开源软件成熟度和社区活跃度**：填写发布时间、开发者、活跃度指标表格
- **1.6 近期发现的安全漏洞**：填写漏洞编号、受影响版本、描述表格
- **1.7 可选择的服务供应商**：列举官方和第三方服务商
- **1.8 供应链风险评估**：评估风险等级并说明原因

### 2. 开源软件使用评估

- **2.1 是否初次引入或版本升级**：标明初次引入或升级版本
- **2.2 代码来源**：填写代码仓库链接表格
- **2.3 升级兼容性**：仅升级情况填写，初次引入填"不涉及"
- **2.4 升级风险和测试方案**：仅升级情况填写，初次引入填"不涉及"
- **2.5 使用范围**：描述业务系统内的使用场景
- **2.6 使用计划**：描述引入时间、用途、后续升级计划

## 生成流程

1. **确定联网搜索工具**: 优先使用 **serpapi-search** skill 进行联网搜索查询GitHub、官方文档、CVE数据库等,如果额度不够再尝试其它
2. **信息收集**：检查用户提供的信息完整性，缺失项主动询问
3. **信息调研**：如需补充技术信息，优先使用 **serpapi-search** skill 进行联网搜索查询GitHub、官方文档、CVE数据库等
4. **模板加载**：加载评估报告模板docx文件
5. **内容填充**：更新表格和段落内容
6. **文件输出**：保存为 `卡中心开源技术引入风险与技术评估报告-{软件名称}.docx`

## 输出规范

- 文件命名：`卡中心开源技术引入风险与技术评估报告-{software_name}.docx`
- 文件格式：Microsoft Word .docx
- 输出位置：用户工作目录或指定路径

## 模板路径

默认模板位置：`template/卡中心开源技术引入风险与技术评估报告-GLM-5.1.docx`（相对于skill目录）

如果没有则让用户提供

## 调用示例

```python
# 使用技能生成报告
from skills.open_source_tech_report import generate_report

data = {
    'software_name': 'GLM-5.1',
    'version': '最新旗舰版',
    'release_date': '2026-04-18',
    'department': '信用卡中心信息技术部',
    'domain': '系统级平台域',
    'project': 'AI原生应用开发平台',
    'rating': 'B',
    'author': '吴思楠',
    'reviewer': '陈远川',
    'license': 'Apache-2.0',
    'developer': '智谱AI/清华大学KEG',
    'github_url': 'https://github.com/THUDM/GLM',
    'necessity': '多场景综合使用...',
    # ... 更多字段
}

output_path = generate_report(template_path, data)
```

## 注意事项

1. 确保所有必填信息完整后再生成报告
2. 安全漏洞信息应查询近期CVE数据库
3. 供应链风险评估需综合考虑：开发者稳定性、社区活跃度、协议合规性、公司资质
4. 类似软件对比应列举2-5个同类产品并简要对比优劣
5. 联网搜索优先使用 serpapi-search skill，获取GitHub信息、官方文档、安全漏洞等资料