<!-- Digimon Evolution: 2026-04-23 | gen:1 -->
---
name: citic-workboard
description: |
  模型推理服务工作看板管理技能。通过CLI交互管理Excel工作项，支持增删改查任务、生成进度报告、日期提醒等功能。
  当用户提到工作项、任务、看板、模型推理服务、进度、任务管理时触发此技能。
allowed-tools: Bash
---

# Skill: citic-workboard

模型推理服务工作看板管理技能。通过CLI交互管理Excel工作项，使用现有HTML看板展示。

## 功能列表

### 任务管理
- **添加任务**: 添加新工作项到指定分类
- **更新状态**: 修改任务状态（未启动/进行中/已完成）
- **更新日期**: 修改开始日期和完成日期
- **更新备注**: 添加或修改任务备注
- **删除任务**: 删除指定行号的任务
- **查询任务**: 根据行号/分类/状态查询任务

### 报告与提醒
- **进度报告**: 生成进度统计报告
- **日期提醒**: 识别超期任务和即将到期任务
- **刷新看板**: 运行workboard.py重新生成HTML

## 文件路径

| 文件 | 位置 |
|-----|------|
| Excel数据文件 | `{workspace}/模型推理服务.xlsx` |
| HTML看板 | `{workspace}/工作看板.html` |
| 生成脚本 | `{workspace}/workboard.py` |
| 工具脚本 | `{skill_dir}/scripts/excel_manager.py` |

## Excel结构

| 列 | 字段 |
|---|------|
| A | 任务编号 |
| B | 任务 |
| C | 任务状态 |
| D | 开始日期 |
| E | 完成日期 |
| F | 交付物 |
| G | 备注 |

## 分类列表

- 一、新模型在华为显卡上部署验证
- 二、新模型在海光显卡上部署验证
- 三、Cosyvoice2 语音模型华为显卡方案
- 四、不同参数模型在海光 BW100上性能测试
- 五、模型在海光显卡上的推理加速方案
- 六、模型在PPU上的性能验证
- 七、技术支撑
- 八、外部
- 里程碑

## 任务状态

- 未启动
- 进行中
- 已完成

## 触发关键词

- 工作项、任务、看板、模型推理服务、进度、任务管理
- add task, update task, delete task
- 任务状态、日期、备注

## 使用示例

### 添加任务
```
用户: 添加任务：部署Qwen3-72B到华为显卡，分类：华为显卡部署
用户: 新增工作项：测试LMCache性能，状态：未启动，备注：需协调资源
```

### 更新状态
```
用户: 把#001任务状态改成进行中
用户: 更新编号001任务状态为已完成
用户: Kimi-k2.5部署任务改为进行中
```

### 更新日期
```
用户: 设置#001开始日期为2026-05-01，完成日期为2026-05-15
用户: 编号010任务日期改成今天到下周
```

### 清除日期
```
用户: 将#005任务的日期置为空
用户: 清除编号010任务的日期
```

### 更新备注
```
用户: 给#001任务备注：资源已协调到位
用户: 编号015添加备注说明延期原因
```

### 删除任务
```
用户: 删除#010任务
用户: 删除编号010的工作项
```

### 查询任务
```
用户: 查看#001任务详情
用户: 查看华为显卡部署分类的所有任务
用户: 显示所有进行中的任务
用户: 有哪些未启动的任务
```

### 进度报告
```
用户: 生成进度报告
用户: 统计各分类完成情况
用户: 查看本周进度
```

### 日期提醒
```
用户: 哪些任务超期了
用户: 查看即将到期的任务
用户: 有什么需要关注的任务
```

### 刷新看板
```
用户: 刷新看板
用户: 更新HTML
用户: 重新生成看板
```

## 工具脚本

### excel_manager.py

位置: `{skill_dir}/scripts/excel_manager.py`

核心函数:
- `init_paths(workspace_dir)` - 初始化路径
- `get_max_task_id()` - 获取最大任务编号
- `get_task_by_id(task_id)` - 按编号获取任务详情
- `get_task_by_row(row)` - 按行号获取任务详情
- `find_row_by_id(task_id)` - 根据编号查找行号
- `add_task(name, category, status, ...)` - 添加任务（自动分配编号）
- `update_task_status(row, status)` - 更新状态
- `update_task_status_by_id(task_id, status)` - 按编号更新状态
- `update_task_dates(row, start_date, end_date)` - 更新日期
- `update_task_dates_by_id(task_id, start_date, end_date)` - 按编号更新日期
- `clear_task_dates(row)` - 清除日期
- `clear_task_dates_by_id(task_id)` - 按编号清除日期
- `update_task_note(row, note)` - 更新备注
- `update_task_note_by_id(task_id, note)` - 按编号更新备注
- `delete_task(row)` - 删除任务
- `delete_task_by_id(task_id)` - 按编号删除任务
- `get_tasks_by_category(category)` - 获取分类任务
- `get_tasks_by_status(status)` - 获取状态任务
- `generate_progress_report()` - 生成进度报告
- `get_overdue_tasks()` - 获取超期任务
- `refresh_board()` - 刷新看板
- `parse_relative_date(date_str)` - 解析相对日期

## 相对日期支持

支持以下相对日期格式:
- 今天、今日、today
- 明天、明日、tomorrow
- 后天
- 下周、下周一
- 下周末
- 月底、月末
- YYYY-MM-DD格式
- MM/DD格式

## 任务标识

使用任务编号标识任务，格式为 `#编号`:
- `#001` 表示编号为 001 的任务
- `#010` 表示编号为 010 的任务

编号格式为三位纯数字 (001, 002, ...)，自动分配且唯一永久保留。删除任务后编号不回收，新任务使用下一个编号。

编号在HTML看板中显示为 `#编号` 格式，便于快速定位。

## 分类匹配

分类名称支持部分匹配:
- "华为显卡" 可匹配 "一、新模型在华为显卡上部署验证"
- "海光显卡" 可匹配 "二、新模型在海光显卡上部署验证"
- "里程碑" 可匹配里程碑分类

## 执行流程

1. 解析用户请求
2. 调用excel_manager.py执行操作
3. 确认变更结果
4. 可选：刷新HTML看板

## 依赖

- openpyxl: Excel文件操作
- pandas: 数据分析
- datetime: 日期处理