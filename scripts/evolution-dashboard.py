#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进化 Dashboard - 可视化展示进化系统状态
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
EVOLUTION_DIR = WORKSPACE / "memory/evolution"
PATTERNS_DIR = WORKSPACE / "memory/patterns"
LEARNINGS_DIR = WORKSPACE / ".learnings"


def count_files(directory, pattern="*.md"):
    """统计文件数量"""
    if not directory.exists():
        return 0
    return len(list(directory.glob(pattern)))


def load_json_file(filepath):
    """加载 JSON 文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}


def get_latest_report_content(directory, prefix):
    """获取最新报告内容"""
    if not directory.exists():
        return None
    
    reports = sorted(directory.glob(f"{prefix}*.md"), reverse=True)
    if reports:
        try:
            return reports[0].read_text(encoding='utf-8')[:500]
        except:
            pass
    return None


def generate_dashboard():
    """生成 Dashboard"""
    dashboard = []
    
    # 标题
    dashboard.append("# 📊 智能进化系统 Dashboard")
    dashboard.append("")
    dashboard.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    dashboard.append(f"**系统版本**: v3.0 (满分版)")
    dashboard.append("")
    
    # 核心指标卡片
    dashboard.append("## 🎯 核心指标")
    dashboard.append("")
    
    # 统计各项数据
    gene_count = count_files(PATTERNS_DIR, "gene-*.md")
    learning_count = count_files(LEARNINGS_DIR)
    report_count = count_files(EVOLUTION_DIR)
    rca_count = count_files(EVOLUTION_DIR / "rca")
    alert_count = count_files(EVOLUTION_DIR / "alerts")
    
    # 加载追踪数据
    tracking_data = load_json_file(EVOLUTION_DIR / "gene-tracking.json")
    genes_tracked = len(tracking_data.get('genes', {}))
    
    # 核心指标
    dashboard.append("| 指标 | 数值 | 状态 |")
    dashboard.append("|------|------|------|")
    dashboard.append(f"| 🧬 Gene 总数 | {gene_count} 个 | ✅ |")
    dashboard.append(f"| 📚 学习记录 | {learning_count} 条 | ✅ |")
    dashboard.append(f"| 📊 进化报告 | {report_count} 份 | ✅ |")
    dashboard.append(f"| 🔍 根因分析 | {rca_count} 份 | ✅ |")
    dashboard.append(f"| 🚨 告警报告 | {alert_count} 份 | ✅ |")
    dashboard.append(f"| 📈 Gene 追踪 | {genes_tracked} 个 | ✅ |")
    dashboard.append("")
    
    # 最新告警
    dashboard.append("## 🚨 最新告警")
    dashboard.append("")
    
    alert_content = get_latest_report_content(EVOLUTION_DIR / "alerts", "predictive-alert")
    if alert_content:
        # 提取告警摘要
        for line in alert_content.split('\n'):
            if '🟠' in line or '🟡' in line or '🟢' in line:
                dashboard.append(f"- {line.strip()}")
    else:
        dashboard.append("- ✅ 无紧急告警")
    dashboard.append("")
    
    # 最近报告
    dashboard.append("## 📄 最近生成的报告")
    dashboard.append("")
    
    all_reports = []
    for pattern in ["*.md", "rca/*.md", "alerts/*.md"]:
        for f in EVOLUTION_DIR.glob(pattern):
            all_reports.append(f)
    
    # 按时间排序，取最新 10 个
    all_reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    for i, report in enumerate(all_reports[:10], 1):
        mtime = datetime.fromtimestamp(report.stat().st_mtime).strftime('%m-%d %H:%M')
        dashboard.append(f"{i}. **{report.name}** - {mtime}")
    dashboard.append("")
    
    # 系统状态
    dashboard.append("## 🖥️ 系统状态")
    dashboard.append("")
    
    # 检查脚本
    scripts_status = []
    scripts = [
        "smart-evolution-master.sh",
        "smart-evolution-lite.py",
        "gene-effect-tracker.py",
        "root-cause-analyzer.py",
        "vector-clustering.py",
        "auto-fix-generator.py",
        "predictive-alerts.py",
    ]
    
    for script in scripts:
        script_path = WORKSPACE / "scripts" / script
        if script_path.exists():
            scripts_status.append(f"- ✅ `{script}`")
        else:
            scripts_status.append(f"- ❌ `{script}`")
    
    dashboard.append("### 核心脚本")
    dashboard.append('\n'.join(scripts_status))
    dashboard.append("")
    
    # 自动修复脚本
    dashboard.append("### 自动修复脚本")
    fix_scripts = list((WORKSPACE / "scripts" / "auto-fixes").glob("*.sh"))
    if fix_scripts:
        for script in fix_scripts:
            dashboard.append(f"- ✅ `{script.name}`")
    else:
        dashboard.append("- ⚠️  无自动修复脚本")
    dashboard.append("")
    
    # 自动化配置
    dashboard.append("### 自动化配置")
    heartbeat_file = WORKSPACE / "HEARTBEAT.md"
    if heartbeat_file.exists():
        content = heartbeat_file.read_text(encoding='utf-8')
        if "smart-evolution-master.sh" in content:
            dashboard.append("- ✅ Cron 已配置（每周一 09:00）")
        else:
            dashboard.append("- ⚠️  Cron 未配置")
    else:
        dashboard.append("- ❌ HEARTBEAT.md 不存在")
    dashboard.append("")
    
    # 下次执行时间
    dashboard.append("### 📅 下次自动执行")
    next_monday = datetime.now()
    days_until_monday = (7 - next_monday.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    next_monday += timedelta(days=days_until_monday)
    next_monday = next_monday.replace(hour=9, minute=0, second=0)
    dashboard.append(f"- **时间**: {next_monday.strftime('%Y-%m-%d %H:%M')}")
    dashboard.append(f"- **命令**: `smart-evolution-master.sh`")
    dashboard.append("")
    
    # 快速操作指南
    dashboard.append("## ⚡ 快速操作")
    dashboard.append("")
    dashboard.append("### 手动执行分析")
    dashboard.append("```bash")
    dashboard.append("~/.openclaw/workspace/scripts/smart-evolution-master.sh")
    dashboard.append("```")
    dashboard.append("")
    
    dashboard.append("### 执行自动修复")
    dashboard.append("```bash")
    dashboard.append("bash ~/.openclaw/workspace/scripts/auto-fixes/fix-api_error.sh")
    dashboard.append("bash ~/.openclaw/workspace/scripts/auto-fixes/fix-data_error.sh")
    dashboard.append("```")
    dashboard.append("")
    
    dashboard.append("### 查看最新报告")
    dashboard.append("```bash")
    dashboard.append("cat ~/.openclaw/workspace/memory/evolution/master-report-$(date +%Y-%m-%d).md")
    dashboard.append("```")
    dashboard.append("")
    
    dashboard.append("---")
    dashboard.append(f"*智能进化系统 Dashboard v1.0 | 让进化可见*")
    
    return '\n'.join(dashboard)


if __name__ == "__main__":
    dashboard = generate_dashboard()
    
    # 保存 Dashboard
    dashboard_file = WORKSPACE / "memory/evolution" / "dashboard.md"
    dashboard_file.write_text(dashboard, encoding='utf-8')
    
    print("✅ Dashboard 已生成")
    print(f"📂 位置：{dashboard_file}")
    print()
    print(dashboard[:2000])
