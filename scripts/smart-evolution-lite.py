#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量智能进化分析系统 - 无需向量数据库，用关键词 + 规则聚类
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

WORKSPACE = Path("/root/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE / ".learnings"
PATTERNS_DIR = WORKSPACE / "memory/patterns"
REPORT_DIR = WORKSPACE / "memory/evolution"

# 错误分类关键词（中文 + 英文）
ERROR_CATEGORIES = {
    "api_error": {
        "keywords": ["API", "接口", "端点", "endpoint", "request", "response", "HTTP", "调用", "返回"],
        "weight": 1.0
    },
    "config_error": {
        "keywords": ["配置", "config", "环境变量", "env", "key", "token", "secret", "密码", "认证"],
        "weight": 1.0
    },
    "logic_error": {
        "keywords": ["逻辑", "条件", "判断", "if", "else", "循环", "loop", "算法", "计算"],
        "weight": 1.0
    },
    "data_error": {
        "keywords": ["数据", "格式", "解析", "parse", "JSON", "XML", "CSV", "数据库", "SQL"],
        "weight": 1.0
    },
    "permission_error": {
        "keywords": ["权限", "permission", "access", "auth", "403", "401", "拒绝", "无权"],
        "weight": 1.0
    },
    "network_error": {
        "keywords": ["网络", "超时", "timeout", "connection", "disconnect", "连接", "断线"],
        "weight": 1.0
    },
    "file_error": {
        "keywords": ["文件", "路径", "path", "read", "write", "IO", "打开", "保存", "下载"],
        "weight": 1.0
    },
    "performance_error": {
        "keywords": ["性能", "慢", "slow", "内存", "memory", "CPU", "卡顿", "优化"],
        "weight": 1.0
    },
}

# 严重度关键词
SEVERITY_KEYWORDS = {
    "critical": {
        "keywords": ["崩溃", "crash", "无法启动", "数据丢失", "security", "安全", "漏洞"],
        "threshold": 1
    },
    "high": {
        "keywords": ["失败", "fail", "错误", "error", "异常", "exception", "报错"],
        "threshold": 1
    },
    "medium": {
        "keywords": ["警告", "warning", "降级", "degraded", "部分", "偶尔"],
        "threshold": 1
    },
    "low": {
        "keywords": ["建议", "优化", "improve", "nice to have", "可以", "最好"],
        "threshold": 1
    },
}

# 解决方案关键词
SOLUTION_KEYWORDS = ["解决", "修复", "fix", "solve", "方案", "方法", "处理", "搞定", "完成"]


def parse_learning_file(file_path):
    """解析学习文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
    except:
        return None
    
    lines = content.strip().split('\n')
    
    # 提取标题
    title = ""
    for line in lines:
        if line.startswith('#'):
            title = line.lstrip('#').strip()
            break
    
    # 提取日期
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
    date_str = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
    
    # 自动分类
    category = classify_error(content)
    
    # 评估严重度
    severity = assess_severity(content)
    
    # 提取关键词
    keywords = extract_keywords(content)
    
    # 提取解决方案
    solution = extract_solution(content)
    
    return {
        "id": f"ERR-{date_str.replace('-', '')}-{hash(title) % 10000:04d}",
        "title": title,
        "date": date_str,
        "category": category,
        "severity": severity,
        "keywords": keywords,
        "solution": solution,
        "content": content[:1500],
        "file": file_path.name,
    }


def classify_error(content):
    """自动分类错误类型"""
    content_lower = content.lower()
    
    scores = {}
    for category, config in ERROR_CATEGORIES.items():
        score = sum(1 for kw in config["keywords"] if kw.lower() in content_lower)
        scores[category] = score
    
    if max(scores.values()) == 0:
        return "unknown"
    
    return max(scores, key=scores.get)


def assess_severity(content):
    """评估严重度"""
    content_lower = content.lower()
    
    for severity, config in SEVERITY_KEYWORDS.items():
        count = sum(1 for kw in config["keywords"] if kw.lower() in content_lower)
        if count >= config["threshold"]:
            return severity
    
    return "medium"


def extract_keywords(content):
    """提取关键词"""
    # 中文 2-4 字词
    chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', content)
    # 英文单词
    english_words = re.findall(r'\b[a-zA-Z]{3,15}\b', content)
    
    # 词频统计
    word_count = Counter()
    stopwords = {'the', 'is', 'are', 'was', 'were', '这个', '那个', '我们', '你们', '可以', '应该'}
    
    for word in chinese_words + english_words:
        word_lower = word.lower()
        if word_lower not in stopwords:
            word_count[word_lower] += 1
    
    return [w for w, _ in word_count.most_common(5)]


def extract_solution(content):
    """提取解决方案"""
    lines = content.split('\n')
    solutions = []
    
    for line in lines:
        if any(kw in line for kw in SOLUTION_KEYWORDS):
            solutions.append(line.strip())
    
    return solutions[:3] if solutions else ["分析错误日志", "定位问题根因", "实施修复方案"]


def cluster_errors(errors, similarity_threshold=0.4):
    """基于关键词相似度聚类"""
    if len(errors) < 2:
        return []
    
    clusters = []
    processed = set()
    
    for i, error in enumerate(errors):
        if error['id'] in processed:
            continue
        
        cluster = [error]
        processed.add(error['id'])
        
        for j, other in enumerate(errors):
            if i == j or other['id'] in processed:
                continue
            
            # 计算关键词相似度
            sim = keyword_similarity(error['keywords'], other['keywords'])
            
            # 分类相同也加分
            if error['category'] == other['category']:
                sim += 0.2
            
            if sim >= similarity_threshold:
                cluster.append(other)
                processed.add(other['id'])
        
        if len(cluster) > 1:
            clusters.append(cluster)
    
    return clusters


def keyword_similarity(kw1, kw2):
    """计算关键词相似度（Jaccard 系数）"""
    if not kw1 or not kw2:
        return 0.0
    
    set1 = set(kw1)
    set2 = set(kw2)
    
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    
    return intersection / union if union > 0 else 0.0


def analyze_root_cause(cluster):
    """分析错误簇的根因"""
    if not cluster:
        return None
    
    all_keywords = []
    categories = Counter()
    dates = []
    all_solutions = []
    
    for error in cluster:
        all_keywords.extend(error['keywords'])
        categories[error['category']] += 1
        dates.append(error['date'])
        all_solutions.extend(error.get('solution', []))
    
    # 高频关键词
    keyword_count = Counter(all_keywords)
    top_keywords = [kw for kw, _ in keyword_count.most_common(5)]
    
    # 主分类
    main_category = categories.most_common(1)[0][0] if categories else "unknown"
    
    return {
        "category": main_category,
        "occurrence_count": len(cluster),
        "top_keywords": top_keywords,
        "date_range": f"{min(dates)} ~ {max(dates)}" if dates else "unknown",
        "affected_files": [e['file'] for e in cluster],
        "common_solutions": list(set(all_solutions))[:3],
    }


def generate_gene_suggestion(root_cause, cluster):
    """自动生成 Gene 建议"""
    category = root_cause['category']
    keywords = root_cause['top_keywords']
    
    # Gene 名称
    gene_id = f"Gene-{category.replace('_', '-').title().replace('-', '')}-{datetime.now().strftime('%Y%m%d')}"
    
    # 触发条件
    trigger_map = {
        "api_error": f"调用 API 出现{'、'.join(keywords[:3])}错误",
        "config_error": f"配置或环境变量出现{'、'.join(keywords[:3])}问题",
        "logic_error": f"代码逻辑出现{'、'.join(keywords[:3])}错误",
        "data_error": f"数据解析或格式出现{'、'.join(keywords[:3])}问题",
        "file_error": f"文件操作出现{'、'.join(keywords[:3])}问题",
        "network_error": f"网络连接出现{'、'.join(keywords[:3])}问题",
    }
    trigger = trigger_map.get(category, f"出现{'、'.join(keywords[:3])}问题")
    
    # 执行步骤
    steps = root_cause.get('common_solutions', [])
    if not steps:
        steps = ["分析错误日志", "定位问题根因", "实施修复方案", "验证修复效果"]
    
    return {
        "gene_id": gene_id,
        "name": f"{category.replace('_', ' ').title()} 处理模式",
        "trigger": trigger,
        "steps": steps,
        "cluster_size": len(cluster),
        "confidence": min(0.9, 0.5 + len(cluster) * 0.1),
    }


def generate_report(errors, clusters, genes):
    """生成报告"""
    report = []
    report.append("# 🧬 智能进化分析报告")
    report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**分析数据**: {len(errors)} 条学习记录")
    report.append("")
    
    # 错误类型分布
    report.append("## 📊 错误类型分布")
    report.append("")
    category_count = Counter(e['category'] for e in errors)
    for cat, count in category_count.most_common():
        report.append(f"- **{cat}**: {count} 个")
    report.append("")
    
    # 严重度分布
    report.append("## ⚠️ 严重度分布")
    report.append("")
    severity_count = Counter(e['severity'] for e in errors)
    emojis = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
    for sev in ['critical', 'high', 'medium', 'low']:
        if sev in severity_count:
            report.append(f"{emojis.get(sev, '⚪')} **{sev}**: {severity_count[sev]} 个")
    report.append("")
    
    # 错误簇分析
    report.append("## 🔍 错误簇分析")
    report.append("")
    if clusters:
        for i, cluster in enumerate(clusters, 1):
            root_cause = analyze_root_cause(cluster)
            report.append(f"### 簇 #{i}: {root_cause['category']}")
            report.append(f"- 出现次数：{root_cause['occurrence_count']}")
            report.append(f"- 关键词：{', '.join(root_cause['top_keywords'])}")
            report.append(f"- 时间范围：{root_cause['date_range']}")
            report.append("")
    else:
        report.append("未发现明显错误簇（错误类型较为分散）")
        report.append("")
    
    # Gene 建议
    report.append("## 💡 自动生成的 Gene 建议")
    report.append("")
    if genes:
        for gene in genes:
            report.append(f"### {gene['gene_id']}: {gene['name']}")
            report.append(f"- **触发条件**: {gene['trigger']}")
            report.append(f"- **置信度**: {gene['confidence']:.0%}")
            report.append(f"- **影响范围**: {gene['cluster_size']} 个错误")
            report.append("- **执行步骤**:")
            for j, step in enumerate(gene['steps'], 1):
                report.append(f"  {j}. {step}")
            report.append("")
    else:
        report.append("暂无新 Gene 建议（已有基因覆盖或错误过于分散）")
        report.append("")
    
    # 行动建议
    report.append("## 🎯 行动建议")
    report.append("")
    if severity_count.get('critical', 0) > 0:
        report.append(f"🔴 **紧急**: 有 {severity_count['critical']} 个严重错误需要立即处理")
    if severity_count.get('high', 0) > 0:
        report.append(f"🟠 **高优**: 有 {severity_count['high']} 个高优错误需要本周处理")
    if genes:
        report.append(f"💡 **建议**: 创建 {len(genes)} 个新 Gene 以覆盖重复错误模式")
    
    report.append("")
    report.append("---")
    report.append(f"*轻量智能模式 | 下次分析：{(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}*")
    
    return '\n'.join(report)


def run():
    """主流程"""
    print("=" * 50)
    print("🧬 轻量智能进化分析系统")
    print("=" * 50)
    print()
    
    # 扫描学习记录
    print("📚 扫描学习记录...")
    errors = []
    if LEARNINGS_DIR.exists():
        for file in LEARNINGS_DIR.glob("*.md"):
            error_data = parse_learning_file(file)
            if error_data:
                errors.append(error_data)
    
    print(f"  ✓ 找到 {len(errors)} 条学习记录")
    print()
    
    if not errors:
        print("⚠️  没有学习记录，跳过分析")
        return
    
    # 聚类
    print("🔍 聚类相似错误...")
    clusters = cluster_errors(errors)
    print(f"  ✓ 发现 {len(clusters)} 个错误簇")
    print()
    
    # 生成 Gene 建议
    print("💡 生成 Gene 建议...")
    genes = []
    for cluster in clusters:
        root_cause = analyze_root_cause(cluster)
        gene = generate_gene_suggestion(root_cause, cluster)
        if gene['confidence'] >= 0.6:
            genes.append(gene)
    
    print(f"  ✓ 生成 {len(genes)} 个 Gene 建议")
    print()
    
    # 生成报告
    print("📝 生成报告...")
    report = generate_report(errors, clusters, genes)
    
    # 保存报告
    REPORT_DIR.mkdir(exist_ok=True)
    report_file = REPORT_DIR / f"smart-report-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"  ✓ 报告已保存：{report_file}")
    print()
    
    # 输出摘要
    print("=" * 50)
    print("📋 分析摘要")
    print("=" * 50)
    print(f"总错误数：{len(errors)}")
    print(f"错误簇数：{len(clusters)}")
    print(f"Gene 建议：{len(genes)}")
    print()
    
    return {
        "total_errors": len(errors),
        "clusters": len(clusters),
        "genes_suggested": len(genes),
        "report_file": str(report_file),
    }


if __name__ == "__main__":
    run()
