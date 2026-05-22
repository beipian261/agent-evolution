# 智能进化系统 - Code Wiki

> 给 AI Agent 装的"自我进化系统"——自动发现问题、自动修复、自动变强

---

## 目录

1. [项目概览](#项目概览)
2. [架构设计](#架构设计)
3. [核心模块](#核心模块)
4. [关键类与函数](#关键类与函数)
5. [依赖关系](#依赖关系)
6. [运行方式](#运行方式)
7. [扩展指南](#扩展指南)

---

## 项目概览

### 项目信息

| 属性 | 值 |
|------|-----|
| 中文名 | 智能进化系统 |
| 版本 | v4.0 |
| 作者 | 爪爪 Zhuazhua |
| 创建时间 | 2026-03-24 |
| GitHub | https://github.com/beipian261/agent-evolution |

### 系统功能

系统主要实现了以下七大核心功能：

1. **智能错误分类** - 自动识别 8 类错误类型
2. **语义聚类** - 基于关键词相似度聚类相似问题
3. **趋势预测** - Prophet 时间序列预测（模块存在，待完善）
4. **根因分析** - 5Why 法自动追问问题根因
5. **自动修复** - 自动生成修复脚本（模块存在，待完善）
6. **Dashboard** - 可视化系统状态（模块存在，待完善）
7. **Gene 效果追踪** - 验证 Gene 创建后的实际效果

---

## 架构设计

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      智能进化系统 v4.0                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Master 主控脚本                        │   │
│  │            (smart-evolution-master.sh)                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌──────────────┬──────────────┬──────────────┬─────────────┐  │
│  │ 错误分析模块  │ Gene追踪模块 │ 根因分析模块 │ ...（其他） │  │
│  └──────────────┴──────────────┴──────────────┴─────────────┘  │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    数据存储层                             │   │
│  │  ┌───────────────────────────────────────────────────┐  │   │
│  │  │  .learnings/ - 学习记录 (Markdown)                │  │   │
│  │  ├───────────────────────────────────────────────────┤  │   │
│  │  │  memory/patterns/ - Gene 库 (可复用方案)          │  │   │
│  │  ├───────────────────────────────────────────────────┤  │   │
│  │  │  memory/evolution/ - 进化报告                     │  │   │
│  │  └───────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 目录结构

```
smart-evolution-system/
├── scripts/                           # 核心脚本目录
│   ├── smart-evolution-master.sh      # 主控脚本
│   ├── smart-evolution-lite.py        # 智能错误分析模块
│   ├── gene-effect-tracker.py         # Gene 效果追踪模块
│   ├── root-cause-analyzer.py         # 根因分析模块
│   ├── vector-clustering.py           # 向量语义聚类（待补充）
│   ├── auto-fix-generator.py          # 自动修复生成（待补充）
│   ├── predictive-alerts.py           # 预测告警（待补充）
│   └── evolution-dashboard.py         # Dashboard（待补充）
├── memory/                            # 数据存储目录
│   ├── patterns/                      # Gene 库
│   │   ├── gene-*.md                  # Gene 文件
│   │   └── README.md                  # Gene 索引
│   └── evolution/                     # 进化报告
│       ├── dashboard.md               # Dashboard
│       ├── smart-report-*.md          # 错误分析报告
│       ├── gene-tracking-*.md         # Gene 效果报告
│       ├── rca-report-*.md            # 根因分析报告
│       ├── alerts/                    # 告警子目录
│       └── rca/                       # 根因分析子目录
├── .learnings/                        # 学习记录（外部输入）
├── README.md                          # 项目说明
└── CODE_WIKI.md                       # 本文档
```

### 核心设计概念

#### 1. Gene（基因）概念

**Gene** 是系统中可复用的解决方案模板，类似于软件设计模式。每个 Gene 包含：

- **Gene ID**: 唯一标识符（如 `Gene-API-20260324`）
- **名称**: 描述性名称
- **触发条件**: 何时应用该 Gene
- **执行步骤**: 具体的解决步骤
- **置信度**: 方案的可靠性评分

#### 2. 工作流

系统的标准工作流程如下：

```
扫描学习记录 → 分类错误 → 聚类相似问题 → 根因分析 → 
生成 Gene 建议 → 追踪 Gene 效果 → 生成报告
```

---

## 核心模块

### 1. Master 主控脚本

**文件**: [smart-evolution-master.sh](file:///workspace/scripts/smart-evolution-master.sh)

**职责**:
- 协调执行所有模块
- 生成汇总报告
- 提供友好的命令行界面

**工作流程**:
1. 初始化环境和目录
2. 执行智能错误分析
3. 执行 Gene 效果追踪
4. 执行根因分析
5. 执行向量语义聚类
6. 执行自动修复生成
7. 执行预测告警
8. 生成 Dashboard
9. 汇总所有模块的执行结果

**关键变量**:
```bash
WORKSPACE="/root/.openclaw/workspace"
SCRIPTS_DIR="$WORKSPACE/scripts"
REPORT_DIR="$WORKSPACE/memory/evolution"
```

---

### 2. 智能错误分析模块

**文件**: [smart-evolution-lite.py](file:///workspace/scripts/smart-evolution-lite.py)

**职责**:
- 解析学习记录文件
- 自动分类错误类型
- 评估严重度
- 聚类相似错误
- 生成 Gene 建议
- 生成错误分析报告

#### 错误分类系统

系统支持 8 种错误类型：

| 错误类型 | 关键词 |
|----------|--------|
| `api_error` | API、接口、端点、endpoint、request、response、HTTP、调用、返回 |
| `config_error` | 配置、config、环境变量、env、key、token、secret、密码、认证 |
| `logic_error` | 逻辑、条件、判断、if、else、循环、loop、算法、计算 |
| `data_error` | 数据、格式、解析、parse、JSON、XML、CSV、数据库、SQL |
| `permission_error` | 权限、permission、access、auth、403、401、拒绝、无权 |
| `network_error` | 网络、超时、timeout、connection、disconnect、连接、断线 |
| `file_error` | 文件、路径、path、read、write、IO、打开、保存、下载 |
| `performance_error` | 性能、慢、slow、内存、memory、CPU、卡顿、优化 |

#### 严重度评估

| 严重度 | 关键词 |
|--------|--------|
| `critical` | 崩溃、crash、无法启动、数据丢失、security、安全、漏洞 |
| `high` | 失败、fail、错误、error、异常、exception、报错 |
| `medium` | 警告、warning、降级、degraded、部分、偶尔 |
| `low` | 建议、优化、improve、nice to have、可以、最好 |

---

### 3. Gene 效果追踪模块

**文件**: [gene-effect-tracker.py](file:///workspace/scripts/gene-effect-tracker.py)

**职责**:
- 扫描 Gene 库
- 统计 Gene 创建前后的错误数量
- 计算错误率下降幅度
- 评估 Gene 效果等级
- 生成效果追踪报告

#### 效果等级定义

| 等级 | 条件 | 描述 |
|------|------|------|
| `highly_effective` | 错误率下降 > 50% | 高效 Gene，效果显著 |
| `effective` | 错误率下降 > 0% | 有效 Gene，有帮助 |
| `no_change` | 错误率无变化 | 需要改进 |
| `negative` | 错误率上升 | 可能有问题 |
| `new_gene` | 新创建，无数据 | 数据收集中 |

#### 计算逻辑

```
错误率下降 = (创建前错误数 - 创建后错误数) / 创建前错误数 × 100%
```

统计时间窗口：创建前 7 天 vs 创建后

---

### 4. 根因分析模块

**文件**: [root-cause-analyzer.py](file:///workspace/scripts/root-cause-analyzer.py)

**职责**:
- 解析学习记录
- 应用 5Why 分析法
- 生成根因分析报告
- 提供系统性改进建议

#### 5Why 模板

针对不同错误类型有定制化的追问模板：

**API 错误**:
1. 为什么 API 调用失败？
2. 为什么端点/参数不正确？
3. 为什么没有提前验证？
4. 为什么文档与实际不一致？
5. 为什么没有自动化测试覆盖？

**配置错误**:
1. 为什么配置错误？
2. 为什么没有配置校验？
3. 为什么环境变量未设置？
4. 为什么部署流程没有检查？
5. 为什么没有配置管理工具？

**数据错误**:
1. 为什么数据格式错误？
2. 为什么没有数据验证？
3. 为什么 API 返回意外结构？
4. 为什么没有容错处理？
5. 为什么没有数据 schema 定义？

---

### 5. 其他模块（待补充）

以下模块在 Master 脚本中有引用，但代码文件尚未完整实现：

- **vector-clustering.py** - 基于向量数据库的语义聚类
- **auto-fix-generator.py** - 自动生成修复脚本
- **predictive-alerts.py** - Prophet 时间序列预测告警
- **evolution-dashboard.py** - 可视化 Dashboard

---

## 关键类与函数

### smart-evolution-lite.py

#### 核心函数

| 函数名 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| `parse_learning_file()` | 解析学习文件 | `file_path: Path` | `dict` 错误数据 |
| `classify_error()` | 自动分类错误 | `content: str` | `str` 分类标签 |
| `assess_severity()` | 评估严重度 | `content: str` | `str` 严重度标签 |
| `extract_keywords()` | 提取关键词 | `content: str` | `List[str]` 关键词列表 |
| `extract_solution()` | 提取解决方案 | `content: str` | `List[str]` 解决方案 |
| `cluster_errors()` | 聚类相似错误 | `errors: List[dict]` | `List[List[dict]]` 聚类结果 |
| `keyword_similarity()` | 计算关键词相似度 | `kw1, kw2: List[str]` | `float` Jaccard 系数 |
| `analyze_root_cause()` | 分析错误簇根因 | `cluster: List[dict]` | `dict` 根因分析结果 |
| `generate_gene_suggestion()` | 生成 Gene 建议 | `root_cause, cluster` | `dict` Gene 建议 |
| `generate_report()` | 生成报告 | `errors, clusters, genes` | `str` Markdown 报告 |
| `run()` | 主流程 | - | `dict` 执行结果 |

#### 关键数据结构

**错误数据**:
```python
{
    "id": "ERR-20260324-1234",
    "title": "API 调用失败",
    "date": "2026-03-24",
    "category": "api_error",
    "severity": "high",
    "keywords": ["api", "调用", "失败"],
    "solution": ["检查端点", "验证参数"],
    "content": "...",
    "file": "learning-2026-03-24.md",
}
```

**Gene 建议**:
```python
{
    "gene_id": "Gene-ApiError-20260324",
    "name": "Api Error 处理模式",
    "trigger": "调用 API 出现错误",
    "steps": [...],
    "cluster_size": 5,
    "confidence": 0.8,
}
```

---

### gene-effect-tracker.py

#### 核心函数

| 函数名 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| `load_tracking_data()` | 加载追踪数据 | - | `dict` 追踪数据 |
| `save_tracking_data()` | 保存追踪数据 | `data: dict` | - |
| `scan_genes()` | 扫描 Gene 库 | - | `List[dict]` Gene 列表 |
| `extract_gene_keywords()` | 提取 Gene 关键词 | `content: str` | `List[str]` 关键词 |
| `scan_learnings()` | 扫描学习记录 | - | `List[dict]` 学习记录 |
| `calculate_gene_effectiveness()` | 计算 Gene 效果 | `gene, learnings` | `dict` 效果数据 |
| `generate_report()` | 生成效果报告 | `tracking_data: dict` | `str` Markdown 报告 |
| `run()` | 主流程 | - | `dict` 执行结果 |

---

### root-cause-analyzer.py

#### 核心函数

| 函数名 | 功能 | 输入 | 输出 |
|--------|------|------|------|
| `parse_learning()` | 解析学习文件 | `file_path: Path` | `dict` 学习数据 |
| `five_whys()` | 生成 5Why 追问链 | `category: str` | `List[str]` 追问列表 |
| `analyze_root_cause()` | 执行根因分析 | `learning: dict` | `dict` 分析结果 |
| `generate_rca_report()` | 生成根因报告 | `analyses: List[dict]` | `str` Markdown 报告 |
| `run()` | 主流程 | - | `dict` 执行结果 |

---

## 依赖关系

### 外部依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| Python 3.7+ | 运行环境 | 系统自带 |
| chromadb (待添加) | 向量数据库 | `pip install chromadb` |
| prophet (待添加) | 时间序列预测 | `pip install prophet` |
| pandas (待添加) | 数据处理 | `pip install pandas` |
| jq | JSON 处理 | `apt-get install jq` |
| curl | HTTP 请求 | `apt-get install curl` |

### 内部模块依赖

```
smart-evolution-master.sh
    ├─→ smart-evolution-lite.py (独立)
    ├─→ gene-effect-tracker.py (独立)
    ├─→ root-cause-analyzer.py (独立)
    ├─→ vector-clustering.py (待实现)
    ├─→ auto-fix-generator.py (待实现)
    ├─→ predictive-alerts.py (待实现)
    └─→ evolution-dashboard.py (待实现)
```

所有 Python 模块目前都是独立运行的，通过文件系统共享数据。

---

## 运行方式

### 环境准备

#### 1. 安装依赖

```bash
# Python 依赖（当前实现只需要标准库）
pip install chromadb prophet pandas  # 未来需要

# 系统依赖
apt-get install jq curl
```

#### 2. 配置工作区

```bash
# 创建工作区目录
mkdir -p ~/.openclaw/workspace
cd ~/.openclaw/workspace

# 复制脚本
cp -r /path/to/smart-evolution-system/scripts/* ~/.openclaw/workspace/scripts/

# 确保脚本可执行
chmod +x ~/.openclaw/workspace/scripts/*.sh
chmod +x ~/.openclaw/workspace/scripts/*.py
```

### 执行完整分析

```bash
# 进入工作区
cd ~/.openclaw/workspace

# 执行完整分析流程
./scripts/smart-evolution-master.sh
```

### 单独运行模块

```bash
# 只运行错误分析
python3 scripts/smart-evolution-lite.py

# 只运行 Gene 效果追踪
python3 scripts/gene-effect-tracker.py

# 只运行根因分析
python3 scripts/root-cause-analyzer.py
```

### 查看结果

```bash
# 查看 Dashboard
cat ~/.openclaw/workspace/memory/evolution/dashboard.md

# 查看最新错误分析报告
ls -t ~/.openclaw/workspace/memory/evolution/smart-report-*.md | head -1 | xargs cat

# 查看 Gene 效果报告
ls -t ~/.openclaw/workspace/memory/evolution/gene-tracking-*.md | head -1 | xargs cat

# 查看根因分析报告
ls -t ~/.openclaw/workspace/memory/evolution/rca/rca-report-*.md | head -1 | xargs cat
```

### 定时任务（可选）

设置每周自动运行：

```bash
# 编辑 crontab
crontab -e

# 添加每周一早上 9 点执行
0 9 * * 1 ~/.openclaw/workspace/scripts/smart-evolution-master.sh >> ~/.openclaw/workspace/logs/cron.log 2>&1
```

---

## 扩展指南

### 添加新的错误分类

在 [smart-evolution-lite.py](file:///workspace/scripts/smart-evolution-lite.py) 中的 `ERROR_CATEGORIES` 字典添加：

```python
ERROR_CATEGORIES = {
    # ... 现有分类
    "your_new_error": {
        "keywords": ["关键词1", "关键词2", "关键词3"],
        "weight": 1.0
    },
}
```

### 添加新的 5Why 模板

在 [root-cause-analyzer.py](file:///workspace/scripts/root-cause-analyzer.py) 中的 `WHY_TEMPLATES` 字典添加：

```python
WHY_TEMPLATES = {
    # ... 现有模板
    "your_new_error": [
        "为什么出现问题1？",
        "为什么出现问题2？",
        "为什么出现问题3？",
        "为什么出现问题4？",
        "为什么出现问题5？",
    ],
}
```

### 实现缺失模块

根据 Master 脚本的引用，创建以下文件并实现相应功能：

1. **vector-clustering.py** - 向量语义聚类
   - 使用 ChromaDB 存储句向量
   - 计算语义相似度
   - 基于向量聚类

2. **auto-fix-generator.py** - 自动修复生成
   - 根据错误类型生成 Shell/Python 修复脚本
   - 输出到 `scripts/auto-fixes/` 目录

3. **predictive-alerts.py** - 预测告警
   - 使用 Prophet 进行时间序列预测
   - 预测未来 7 天的错误趋势
   - 生成告警报告

4. **evolution-dashboard.py** - Dashboard
   - 汇总所有模块的数据
   - 生成可视化 Markdown 报告

### 贡献代码

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 常见问题

### Q: 系统需要哪些输入数据？

A: 系统需要在 `.learnings/` 目录下有 Markdown 格式的学习记录文件。文件名建议包含日期，如 `learning-2026-03-24.md`。

### Q: 如何创建一个 Gene？

A: Gene 是 Markdown 文件，放在 `memory/patterns/` 目录下。建议包含以下内容：
- 标题（#）
- 创建时间
- 触发条件
- 执行步骤

### Q: 系统是如何判断 Gene 效果的？

A: 系统通过对比 Gene 创建前 7 天和创建后相同类型错误的数量变化来评估效果。

---

## 更新日志

### v4.0 (2026-03-24)
- 新增 Prophet 时间序列预测框架
- 新增 Dashboard 可视化框架
- 新增自动回滚机制规划
- 新增 Gene 库索引

### v3.0 (2026-03-24)
- 新增向量语义聚类框架
- 新增自动修复生成框架

### v2.0 (2026-03-24)
- 新增 Gene 效果追踪模块
- 新增根因分析模块 (5Why)

### v1.0 (2026-03-24)
- 初始版本：错误分类 + 聚类 + Gene 生成

---

## 许可证

MIT License

---

*最后更新: 2026-05-22*
