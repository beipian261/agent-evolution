#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能根因分析 - 5Why 法自动追问根因
"""

import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE / ".learnings"
ANALYSIS_DIR = WORKSPACE / "memory/evolution/rca"  # Root Cause Analysis


# 5Why 追问模板
WHY_TEMPLATES = {
    "api_error": [
        "为什么 API 调用失败？",
        "为什么端点/参数不正确？",
        "为什么没有提前验证？",
        "为什么文档与实际不一致？",
        "为什么没有自动化测试覆盖？",
    ],
    "config_error": [
        "为什么配置错误？",
        "为什么没有配置校验？",
        "为什么环境变量未设置？",
        "为什么部署流程没有检查？",
        "为什么没有配置管理工具？",
    ],
    "data_error": [
        "为什么数据格式错误？",
        "为什么没有数据验证？",
        "为什么 API 返回意外结构？",
        "为什么没有容错处理？",
        "为什么没有数据 schema 定义？",
    ],
    "logic_error": [
        "为什么逻辑错误？",
        "为什么边界条件未考虑？",
        "为什么没有单元测试？",
        "为什么代码审查没发现？",
        "为什么没有自动化测试？",
    ],
    "permission_error": [
        "为什么权限不足？",
        "为什么账号未授权？",
        "为什么权限流程不清晰？",
        "为什么没有权限检查清单？",
        "为什么没有自动化权限验证？",
    ],
    "default": [
        "为什么出现这个问题？",
        "为什么没有提前预防？",
        "为什么流程有漏洞？",
        "为什么没有检查机制？",
        "为什么没有自动化保障？",
    ],
}


def parse_learning(file_path):
    """解析学习文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
    except:
        return None
    
    # 提取标题
    title = ""
    for line in content.split('\n'):
        if line.startswith('#'):
            title = line.lstrip('#').strip()
            break
    
    # 提取分类
    category = "unknown"
    category_patterns = {
        "api_error": ["API", "接口", "端点", "HTTP"],
        "config_error": ["配置", "config", "环境变量"],
        "data_error": ["数据", "格式", "解析", "JSON"],
        "logic_error": ["逻辑", "条件", "算法"],
        "permission_error": ["权限", "授权", "认证"],
    }
    
    for cat, keywords in category_patterns.items():
        if any(kw.lower() in content.lower() for kw in keywords):
            category = cat
            break
    
    return {
        "file": file_path.name,
        "title": title,
        "category": category,
        "content": content,
    }


def five_whys(category):
    """生成 5Why 追问链"""
    return WHY_TEMPLATES.get(category, WHY_TEMPLATES["default"])


def analyze_root_cause(learning):
    """执行根因分析"""
    category = learning['category']
    why_chain = five_whys(category)
    
    # 从内容中提取可能的答案
    content = learning['content']
    
    analysis = {
        "problem": learning['title'],
        "category": category,
        "why_chain": [],
        "root_cause": "",
        "preventive_actions": [],
    }
    
    # 模拟 5Why 分析（简化版）
    for i, why in enumerate(why_chain, 1):
        analysis['why_chain'].append({
            "level": i,
            "why": why,
            "answer": None,  # 需要人工填写或更高级的 AI 分析
        })
    
    # 从内容中提取根因线索
    root_cause_patterns = [
        (r"根因 [：:]\s*(.+)", "根因"),
        (r"原因 [：:]\s*(.+)", "原因"),
        (r"问题 [：:]\s*(.+)", "问题"),
        (r"因为\s*(.+?)[。,.!]", "因为"),
    ]
    
    for pattern, label in root_cause_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            analysis['root_cause'] = match.group(1).strip()
            break
    
    # 从内容中提取预防措施
    preventive_patterns = [
        r"预防[：:]\s*(.+)",
        r"避免[：:]\s*(.+)",
        r"下次\s*(.+)",
        r"建议[：:]\s*(.+)",
    ]
    
    for pattern in preventive_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            analysis['preventive_actions'].append(match.strip())
    
    return analysis


def generate_rca_report(analyses):
    """生成根因分析报告"""
    report = []
    report.append("# 🔍 根因分析报告 (5Why)")
    report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**分析数量**: {len(analyses)}")
    report.append("")
    
    # 按分类统计
    category_count = {}
    for a in analyses:
        cat = a.get('category', 'unknown')
        category_count[cat] = category_count.get(cat, 0) + 1
    
    report.append("## 📊 问题分类统计")
    report.append("")
    for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
        report.append(f"- **{cat}**: {count} 个")
    report.append("")
    
    # 详细分析
    report.append("## 🔬 详细根因分析")
    report.append("")
    
    for i, analysis in enumerate(analyses[:10], 1):  # 只显示前 10 个
        report.append(f"### #{i}: {analysis['problem'][:50]}...")
        report.append(f"- **分类**: {analysis['category']}")
        report.append(f"- **根因**: {analysis.get('root_cause', '待分析')}")
        report.append("")
        
        # 5Why 链（简化展示）
        report.append("**5Why 追问链**:")
        for why_item in analysis['why_chain'][:3]:  # 只展示前 3 个 Why
            report.append(f"  - Q{why_item['level']}: {why_item['why']}")
        report.append("")
        
        # 预防措施
        if analysis['preventive_actions']:
            report.append("**预防措施**:")
            for action in analysis['preventive_actions'][:3]:
                report.append(f"  - {action}")
        report.append("")
    
    # 改进建议
    report.append("## 💡 系统性改进建议")
    report.append("")
    
    if category_count.get('api_error', 0) > 2:
        report.append("### API 错误频发")
        report.append("- 建立 API 调用封装层，统一错误处理")
        report.append("- 添加 API 端点自动化测试")
        report.append("- 维护 API 变更日志，及时更新调用代码")
        report.append("")
    
    if category_count.get('config_error', 0) > 2:
        report.append("### 配置错误频发")
        report.append("- 使用配置管理工具（如 pydantic-settings）")
        report.append("- 添加配置启动校验")
        report.append("- 文档化所有必需配置项")
        report.append("")
    
    if category_count.get('data_error', 0) > 2:
        report.append("### 数据错误频发")
        report.append("- 定义数据 Schema（如 Pydantic 模型）")
        report.append("- 添加数据验证层")
        report.append("- 实现优雅的降级处理")
        report.append("")
    
    report.append("---")
    report.append(f"*5Why 分析法 | 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    
    return '\n'.join(report)


def run():
    """主流程"""
    print("=" * 50)
    print("🔍 智能根因分析系统 (5Why)")
    print("=" * 50)
    print()
    
    # 扫描学习记录
    print("📚 扫描学习记录...")
    analyses = []
    if LEARNINGS_DIR.exists():
        for file in LEARNINGS_DIR.glob("*.md"):
            learning = parse_learning(file)
            if learning:
                analysis = analyze_root_cause(learning)
                analyses.append(analysis)
    
    print(f"  ✓ 分析 {len(analyses)} 条学习记录")
    print()
    
    # 生成报告
    print("📝 生成根因分析报告...")
    report = generate_rca_report(analyses)
    
    ANALYSIS_DIR.mkdir(exist_ok=True)
    report_file = ANALYSIS_DIR / f"rca-report-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"  ✓ 报告已保存：{report_file}")
    print()
    
    # 输出摘要
    print("=" * 50)
    print("📋 分析摘要")
    print("=" * 50)
    
    # 分类统计
    category_count = {}
    for a in analyses:
        cat = a.get('category', 'unknown')
        category_count[cat] = category_count.get(cat, 0) + 1
    
    for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
        print(f"{cat}: {count} 个")
    
    print()
    
    return {
        "total_analyses": len(analyses),
        "report_file": str(report_file),
    }


if __name__ == "__main__":
    run()
