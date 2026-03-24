#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gene 效果追踪系统 - 验证 Gene 创建后是否真的减少了错误
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/root/.openclaw/workspace")
PATTERNS_DIR = WORKSPACE / "memory/patterns"
LEARNINGS_DIR = WORKSPACE / ".learnings"
TRACKING_FILE = WORKSPACE / "memory/evolution/gene-tracking.json"


def load_tracking_data():
    """加载追踪数据"""
    if TRACKING_FILE.exists():
        with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "genes": {},
        "last_updated": None,
    }


def save_tracking_data(data):
    """保存追踪数据"""
    data["last_updated"] = datetime.now().isoformat()
    TRACKING_FILE.parent.mkdir(exist_ok=True)
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def scan_genes():
    """扫描所有 Gene"""
    genes = []
    if not PATTERNS_DIR.exists():
        return genes
    
    for file in PATTERNS_DIR.glob("gene-*.md"):
        try:
            content = file.read_text(encoding='utf-8')
            
            # 提取 Gene ID（从文件名）
            gene_id = file.stem  # gene-API-001
            
            # 提取创建时间
            create_match = re.search(r'\*\*创建时间\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
            create_date = create_match.group(1) if create_match else datetime.now().strftime('%Y-%m-%d')
            
            # 提取触发条件
            trigger_match = re.search(r'\*\*触发条件\*\*:\s*(.+)', content)
            trigger = trigger_match.group(1).strip() if trigger_match else "未知"
            
            # 提取关键词（从内容中提取技术关键词）
            keywords = extract_gene_keywords(content)
            
            genes.append({
                "gene_id": gene_id,
                "file": file.name,
                "create_date": create_date,
                "trigger": trigger,
                "keywords": keywords,
            })
        except Exception as e:
            print(f"  ⚠️  读取失败 {file.name}: {e}")
    
    return genes


def extract_gene_keywords(content):
    """从 Gene 内容提取关键词"""
    keywords = []
    
    # 提取技术关键词
    tech_patterns = [
        r'API', r'HTTP', r'JSON', r'POST', r'GET',
        r'端点', r'配置', r'权限', r'数据', r'文件',
    ]
    
    for pattern in tech_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            keywords.append(pattern.lower())
    
    return keywords


def scan_learnings():
    """扫描学习记录"""
    learnings = []
    if not LEARNINGS_DIR.exists():
        return learnings
    
    for file in LEARNINGS_DIR.glob("*.md"):
        try:
            content = file.read_text(encoding='utf-8')
            
            # 提取日期
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file.name)
            date_str = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
            
            # 提取标题
            title = ""
            for line in content.split('\n'):
                if line.startswith('#'):
                    title = line.lstrip('#').strip()
                    break
            
            # 提取关键词
            keywords = []
            tech_words = ['API', 'HTTP', 'JSON', '配置', '权限', '数据', '文件', '网络']
            for word in tech_words:
                if word.lower() in content.lower():
                    keywords.append(word.lower())
            
            learnings.append({
                "file": file.name,
                "date": date_str,
                "title": title,
                "keywords": keywords,
            })
        except:
            pass
    
    return learnings


def calculate_gene_effectiveness(gene, learnings):
    """计算 Gene 效果"""
    create_date = gene['create_date']
    gene_keywords = gene['keywords']
    
    if not gene_keywords:
        return None
    
    # 创建前的错误数（创建前 7 天）
    try:
        create_dt = datetime.strptime(create_date, '%Y-%m-%d')
        before_start = (create_dt - timedelta(days=7)).strftime('%Y-%m-%d')
        after_start = create_date
    except:
        return None
    
    errors_before = 0
    errors_after = 0
    
    for learning in learnings:
        # 检查是否匹配 Gene 的关键词
        match = any(kw in learning['keywords'] for kw in gene_keywords)
        if not match:
            continue
        
        # 统计创建前后的错误数
        if learning['date'] < before_start:
            errors_before += 1
        elif learning['date'] >= after_start:
            errors_after += 1
    
    # 计算效果
    if errors_before == 0:
        effectiveness = "new_gene"  # 新 Gene，尚无数据
    else:
        reduction = (errors_before - errors_after) / errors_before * 100
        if reduction > 50:
            effectiveness = "highly_effective"
        elif reduction > 0:
            effectiveness = "effective"
        elif reduction == 0:
            effectiveness = "no_change"
        else:
            effectiveness = "negative"
    
    return {
        "errors_before": errors_before,
        "errors_after": errors_after,
        "reduction_rate": max(0, reduction) if errors_before > 0 else 0,
        "effectiveness": effectiveness,
    }


def generate_report(tracking_data):
    """生成效果报告"""
    report = []
    report.append("# 📊 Gene 效果追踪报告")
    report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**追踪 Gene 数**: {len(tracking_data['genes'])}")
    report.append("")
    
    # 按效果分类
    highly_effective = []
    effective = []
    no_change = []
    new_genes = []
    
    for gene_id, data in tracking_data['genes'].items():
        eff = data.get('effectiveness', 'unknown')
        if eff == 'highly_effective':
            highly_effective.append((gene_id, data))
        elif eff == 'effective':
            effective.append((gene_id, data))
        elif eff == 'no_change' or eff == 'negative':
            no_change.append((gene_id, data))
        else:
            new_genes.append((gene_id, data))
    
    # 高效 Gene
    report.append("## 🌟 高效 Gene（错误率降 50%+）")
    report.append("")
    if highly_effective:
        for gene_id, data in highly_effective:
            report.append(f"### {gene_id}")
            report.append(f"- 创建时间：{data.get('create_date', '未知')}")
            report.append(f"- 创建前错误：{data.get('errors_before', 0)} 个")
            report.append(f"- 创建后错误：{data.get('errors_after', 0)} 个")
            report.append(f"- 错误率下降：{data.get('reduction_rate', 0):.0f}%")
            report.append("")
    else:
        report.append("暂无高效 Gene（需要更多运行数据）")
        report.append("")
    
    # 有效 Gene
    report.append("## ✅ 有效 Gene（错误率有下降）")
    report.append("")
    if effective:
        for gene_id, data in effective:
            report.append(f"- **{gene_id}**: 错误率下降 {data.get('reduction_rate', 0):.0f}%")
    else:
        report.append("暂无")
    report.append("")
    
    # 无变化 Gene
    report.append("## ⚠️ 需要改进的 Gene（错误率无变化或上升）")
    report.append("")
    if no_change:
        for gene_id, data in no_change:
            report.append(f"- **{gene_id}**: 创建前 {data.get('errors_before', 0)} 个，创建后 {data.get('errors_after', 0)} 个")
        report.append("")
        report.append("**建议**: 检查 Gene 是否被正确执行，或更新执行步骤")
    else:
        report.append("暂无")
    report.append("")
    
    # 新 Gene
    report.append("## 🆕 新 Gene（数据收集中）")
    report.append("")
    if new_genes:
        for gene_id, data in new_genes:
            report.append(f"- **{gene_id}**: {data.get('create_date', '未知')} 创建")
    else:
        report.append("暂无")
    report.append("")
    
    # 总体统计
    report.append("## 📈 总体效果")
    report.append("")
    total = len(tracking_data['genes'])
    if total > 0:
        effective_count = len(highly_effective) + len(effective)
        report.append(f"- 总 Gene 数：{total}")
        report.append(f"- 有效 Gene 数：{effective_count} ({effective_count/total*100:.0f}%)")
        report.append(f"- 待改进 Gene 数：{len(no_change)} ({len(no_change)/total*100:.0f}%)")
    else:
        report.append("暂无数据")
    report.append("")
    
    report.append("---")
    report.append(f"*数据截止：{tracking_data.get('last_updated', '首次运行')}*")
    
    return '\n'.join(report)


def run():
    """主流程"""
    print("=" * 50)
    print("📊 Gene 效果追踪系统")
    print("=" * 50)
    print()
    
    # 加载现有数据
    print("📂 加载追踪数据...")
    tracking_data = load_tracking_data()
    print(f"  ✓ 已加载 {len(tracking_data.get('genes', {}))} 个 Gene 记录")
    print()
    
    # 扫描 Gene
    print("🔍 扫描 Gene 库...")
    genes = scan_genes()
    print(f"  ✓ 发现 {len(genes)} 个 Gene")
    print()
    
    # 扫描学习记录
    print("📚 扫描学习记录...")
    learnings = scan_learnings()
    print(f"  ✓ 发现 {len(learnings)} 条学习记录")
    print()
    
    # 计算每个 Gene 的效果
    print("📈 计算 Gene 效果...")
    for gene in genes:
        gene_id = gene['gene_id']
        
        # 如果是新 Gene，初始化
        if gene_id not in tracking_data['genes']:
            tracking_data['genes'][gene_id] = {
                "gene_id": gene_id,
                "create_date": gene['create_date'],
                "trigger": gene['trigger'],
                "first_tracked": datetime.now().strftime('%Y-%m-%d'),
            }
        
        # 计算效果
        effectiveness = calculate_gene_effectiveness(gene, learnings)
        if effectiveness:
            tracking_data['genes'][gene_id].update(effectiveness)
            eff_label = effectiveness.get('effectiveness', 'unknown')
            print(f"  - {gene_id}: {eff_label}")
    
    print()
    
    # 保存数据
    print("💾 保存追踪数据...")
    save_tracking_data(tracking_data)
    print(f"  ✓ 已保存到：{TRACKING_FILE}")
    print()
    
    # 生成报告
    print("📝 生成报告...")
    report = generate_report(tracking_data)
    report_file = WORKSPACE / "memory/evolution" / f"gene-tracking-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.parent.mkdir(exist_ok=True)
    report_file.write_text(report, encoding='utf-8')
    print(f"  ✓ 报告已保存：{report_file}")
    print()
    
    # 输出摘要
    print("=" * 50)
    print("📋 追踪摘要")
    print("=" * 50)
    
    # 统计效果分布
    eff_counts = defaultdict(int)
    for data in tracking_data['genes'].values():
        eff = data.get('effectiveness', 'unknown')
        eff_counts[eff] += 1
    
    print(f"高效 Gene: {eff_counts.get('highly_effective', 0)} 个")
    print(f"有效 Gene: {eff_counts.get('effective', 0)} 个")
    print(f"无变化 Gene: {eff_counts.get('no_change', 0)} 个")
    print(f"新 Gene: {eff_counts.get('new_gene', 0)} 个")
    print()
    
    return {
        "total_genes": len(tracking_data['genes']),
        "report_file": str(report_file),
    }


if __name__ == "__main__":
    run()
