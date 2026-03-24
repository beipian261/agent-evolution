#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能进化分析系统 - 自动化错误聚类、根因分析、Gene 生成
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import re

# ChromaDB
import chromadb
from chromadb.config import Settings

WORKSPACE = Path("/root/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE / ".learnings"
PATTERNS_DIR = WORKSPACE / "memory/patterns"
DB_DIR = WORKSPACE / ".chroma_db"

# 错误类型分类体系
ERROR_CATEGORIES = {
    "api_error": ["API", "接口", "端点", "endpoint", "request", "response"],
    "config_error": ["配置", "config", "环境变量", "env", "key", "token"],
    "logic_error": ["逻辑", "条件", "判断", "if", "else", "循环", "loop"],
    "data_error": ["数据", "格式", "解析", "parse", "JSON", "XML"],
    "permission_error": ["权限", "permission", "access", "auth", "403", "401"],
    "network_error": ["网络", "超时", "timeout", "connection", "disconnect"],
    "file_error": ["文件", "路径", "path", "read", "write", "IO"],
    "performance_error": ["性能", "慢", "slow", "内存", "memory", "CPU"],
}

# 严重度关键词
SEVERITY_KEYWORDS = {
    "critical": ["崩溃", "crash", "无法启动", "数据丢失", "security"],
    "high": ["失败", "fail", "错误", "error", "异常"],
    "medium": ["警告", "warning", "降级", "degraded"],
    "low": ["建议", "优化", "improve", "nice to have"],
}


class IntelligentEvolutionAnalyzer:
    """智能进化分析器"""
    
    def __init__(self):
        self.db_dir = DB_DIR
        self.db_dir.mkdir(exist_ok=True)
        
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_dir))
        self.collection = self.client.get_or_create_collection(
            name="errors",
            metadata={"description": "错误日志向量库"}
        )
        
        self.errors_data = []
        
    def scan_learnings(self):
        """扫描学习记录，提取结构化数据"""
        print("📚 扫描学习记录...")
        
        errors = []
        for file in LEARNINGS_DIR.glob("*.md"):
            try:
                content = file.read_text(encoding='utf-8')
                error_data = self._parse_learning_file(file, content)
                if error_data:
                    errors.append(error_data)
            except Exception as e:
                print(f"  ⚠️  解析失败 {file.name}: {e}")
        
        self.errors_data = errors
        print(f"  ✓ 找到 {len(errors)} 条学习记录")
        return errors
    
    def _parse_learning_file(self, file_path, content):
        """解析学习文件，提取结构化数据"""
        lines = content.strip().split('\n')
        
        # 提取标题
        title = ""
        for line in lines:
            if line.startswith('#'):
                title = line.lstrip('#').strip()
                break
        
        # 提取日期（从文件名或内容）
        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
        date_str = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
        
        # 自动分类
        category = self._auto_classify(content)
        
        # 自动评估严重度
        severity = self._assess_severity(content)
        
        # 提取关键词
        keywords = self._extract_keywords(content)
        
        # 生成唯一 ID（使用文件路径 + 标题确保唯一）
        unique_str = f"{file_path.name}:{title}"
        error_id = f"ERR-{date_str.replace('-', '')}-{hashlib.md5(unique_str.encode()).hexdigest()[:6].upper()}"
        
        return {
            "id": error_id,
            "title": title,
            "date": date_str,
            "category": category,
            "severity": severity,
            "keywords": keywords,
            "content": content[:2000],  # 限制长度
            "file": file_path.name,
            "embedding_text": f"{title} {content[:500]}",  # 用于向量嵌入
        }
    
    def _auto_classify(self, content):
        """自动分类错误类型"""
        content_lower = content.lower()
        
        scores = {}
        for category, keywords in ERROR_CATEGORIES.items():
            score = sum(1 for kw in keywords if kw.lower() in content_lower)
            scores[category] = score
        
        if max(scores.values()) == 0:
            return "unknown"
        
        return max(scores, key=scores.get)
    
    def _assess_severity(self, content):
        """自动评估严重度"""
        content_lower = content.lower()
        
        for severity, keywords in SEVERITY_KEYWORDS.items():
            if any(kw.lower() in content_lower for kw in keywords):
                return severity
        
        return "medium"
    
    def _extract_keywords(self, content):
        """提取关键词（简化版）"""
        # 中文关键词：2-4 个字符的连续词
        chinese_words = re.findall(r'[\u4e00-\u9fa5]{2,4}', content)
        # 英文关键词：字母组成的单词
        english_words = re.findall(r'\b[a-zA-Z]{3,15}\b', content)
        
        # 统计词频
        word_count = {}
        for word in chinese_words + english_words:
            word_lower = word.lower()
            # 跳过常见停用词
            if word_lower in ['the', 'is', 'are', 'was', 'were', '这个', '那个', '我们', '你们']:
                continue
            word_count[word_lower] = word_count.get(word_lower, 0) + 1
        
        # 返回 Top 5 关键词
        sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
        return [w[0] for w in sorted_words[:5]]
    
    def build_vector_index(self):
        """构建向量索引"""
        print("🔧 构建向量索引...")
        
        # 清空旧数据
        try:
            existing = self.collection.get()
            if existing['ids']:
                self.collection.delete(ids=existing['ids'])
        except:
            pass
        
        # 添加新数据
        if self.errors_data:
            # 使用 ChromaDB 的内置嵌入（不需要额外模型）
            documents = [e['embedding_text'] for e in self.errors_data]
            ids = [e['id'] for e in self.errors_data]
            metadatas = [
                {
                    "category": e['category'],
                    "severity": e['severity'],
                    "date": e['date'],
                    "title": e['title'][:100],
                }
                for e in self.errors_data
            ]
            
            self.collection.add(
                documents=documents,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"  ✓ 索引 {len(self.errors_data)} 条错误")
    
    def cluster_errors(self, threshold=0.7):
        """聚类相似错误"""
        print("🔍 聚类相似错误...")
        
        if len(self.errors_data) < 2:
            print("  ⚠️  数据不足，跳过聚类")
            return []
        
        clusters = []
        processed = set()
        
        for i, error in enumerate(self.errors_data):
            if error['id'] in processed:
                continue
            
            # 查询相似错误
            results = self.collection.query(
                query_documents=[error['embedding_text']],
                n_results=min(10, len(self.errors_data)),
                include=["distances", "metadatas", "documents"]
            )
            
            # 收集相似错误（距离 < threshold）
            cluster = [error]
            processed.add(error['id'])
            
            if results['ids'] and results['ids'][0]:
                for j, (id_, distance, meta) in enumerate(zip(
                    results['ids'][0],
                    results['distances'][0],
                    results['metadatas'][0]
                )):
                    if id_ != error['id'] and distance < threshold:
                        similar_error = next(
                            (e for e in self.errors_data if e['id'] == id_),
                            None
                        )
                        if similar_error:
                            cluster.append(similar_error)
                            processed.add(id_)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        print(f"  ✓ 发现 {len(clusters)} 个错误簇")
        return clusters
    
    def analyze_root_cause(self, cluster):
        """分析错误簇的根因"""
        if not cluster:
            return None
        
        # 提取共同模式
        all_keywords = []
        categories = {}
        dates = []
        
        for error in cluster:
            all_keywords.extend(error['keywords'])
            cat = error['category']
            categories[cat] = categories.get(cat, 0) + 1
            dates.append(error['date'])
        
        # 统计高频关键词
        keyword_count = {}
        for kw in all_keywords:
            keyword_count[kw] = keyword_count.get(kw, 0) + 1
        
        top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # 主分类
        main_category = max(categories, key=categories.get)
        
        # 时间跨度
        date_range = f"{min(dates)} ~ {max(dates)}"
        
        return {
            "category": main_category,
            "occurrence_count": len(cluster),
            "top_keywords": [kw[0] for kw in top_keywords],
            "date_range": date_range,
            "affected_files": [e['file'] for e in cluster],
        }
    
    def generate_gene_suggestion(self, root_cause, cluster):
        """自动生成 Gene 建议"""
        category = root_cause['category']
        keywords = root_cause['top_keywords']
        
        # 生成 Gene 名称
        gene_name = f"Gene-{category.replace('_', '-').title().replace('-', '')}-{datetime.now().strftime('%Y%m%d')}"
        
        # 生成触发条件
        trigger_conditions = {
            "api_error": f"调用 API 出现{'、'.join(keywords[:3])}错误",
            "config_error": f"配置文件或环境变量出现{'、'.join(keywords[:3])}问题",
            "logic_error": f"代码逻辑出现{'、'.join(keywords[:3])}错误",
            "data_error": f"数据解析或格式出现{'、'.join(keywords[:3])}问题",
        }
        trigger = trigger_conditions.get(category, f"出现{'、'.join(keywords[:3])}问题")
        
        # 生成执行步骤（从错误解决方案提取）
        steps = []
        for i, error in enumerate(cluster[:3], 1):
            # 简单提取解决方案（假设在内容中包含"解决"、"修复"等词的句子）
            content_lines = error['content'].split('\n')
            for line in content_lines:
                if any(kw in line for kw in ['解决', '修复', 'fix', 'solve', '方案']):
                    steps.append(line.strip())
                    break
        
        if not steps:
            steps = ["分析错误日志", "定位问题根因", "实施修复方案", "验证修复效果"]
        
        return {
            "gene_id": gene_name,
            "name": f"{category.replace('_', ' ').title()} 处理模式",
            "trigger": trigger,
            "steps": steps,
            "cluster_size": len(cluster),
            "confidence": min(0.9, 0.5 + len(cluster) * 0.1),  # 簇越大，置信度越高
        }
    
    def generate_report(self, clusters, genes):
        """生成智能分析报告"""
        report = []
        report.append("# 🧬 智能进化分析报告")
        report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**分析数据**: {len(self.errors_data)} 条学习记录")
        report.append("")
        
        # 错误分布
        report.append("## 📊 错误类型分布")
        report.append("")
        category_count = {}
        for error in self.errors_data:
            cat = error['category']
            category_count[cat] = category_count.get(cat, 0) + 1
        
        for cat, count in sorted(category_count.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{cat}**: {count} 个")
        report.append("")
        
        # 严重度分布
        report.append("## ⚠️ 严重度分布")
        report.append("")
        severity_count = {}
        for error in self.errors_data:
            sev = error['severity']
            severity_count[sev] = severity_count.get(sev, 0) + 1
        
        for sev in ['critical', 'high', 'medium', 'low']:
            if sev in severity_count:
                emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[sev]
                report.append(f"{emoji} **{sev}**: {severity_count[sev]} 个")
        report.append("")
        
        # 错误簇分析
        report.append("## 🔍 错误簇分析")
        report.append("")
        if clusters:
            for i, cluster in enumerate(clusters, 1):
                root_cause = self.analyze_root_cause(cluster)
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
        critical_count = severity_count.get('critical', 0)
        high_count = severity_count.get('high', 0)
        
        if critical_count > 0:
            report.append(f"🔴 **紧急**: 有 {critical_count} 个严重错误需要立即处理")
        if high_count > 0:
            report.append(f"🟠 **高优**: 有 {high_count} 个高优错误需要本周处理")
        if genes:
            report.append(f"💡 **建议**: 创建 {len(genes)} 个新 Gene 以覆盖重复错误模式")
        
        report.append("")
        report.append("---")
        report.append(f"*智能生成 | 下次分析：{(datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')}*")
        
        return '\n'.join(report)
    
    def run(self):
        """执行完整分析流程"""
        print("=" * 50)
        print("🧬 智能进化分析系统")
        print("=" * 50)
        print()
        
        # 1. 扫描学习记录
        self.scan_learnings()
        print()
        
        # 2. 构建向量索引
        self.build_vector_index()
        print()
        
        # 3. 聚类相似错误
        clusters = self.cluster_errors()
        print()
        
        # 4. 分析根因并生成 Gene 建议
        genes = []
        for cluster in clusters:
            root_cause = self.analyze_root_cause(cluster)
            gene = self.generate_gene_suggestion(root_cause, cluster)
            if gene['confidence'] >= 0.6:  # 只推荐高置信度的
                genes.append(gene)
        
        print(f"💡 生成 {len(genes)} 个 Gene 建议")
        print()
        
        # 5. 生成报告
        report = self.generate_report(clusters, genes)
        
        # 保存报告
        report_file = WORKSPACE / "memory/evolution" / f"smart-report-{datetime.now().strftime('%Y-%m-%d')}.md"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report, encoding='utf-8')
        
        print(f"✅ 报告已保存：{report_file}")
        print()
        
        # 输出摘要
        print("=" * 50)
        print("📋 分析摘要")
        print("=" * 50)
        print(f"总错误数：{len(self.errors_data)}")
        print(f"错误簇数：{len(clusters)}")
        print(f"Gene 建议：{len(genes)}")
        print()
        
        return {
            "total_errors": len(self.errors_data),
            "clusters": len(clusters),
            "genes_suggested": len(genes),
            "report_file": str(report_file),
        }


if __name__ == "__main__":
    analyzer = IntelligentEvolutionAnalyzer()
    analyzer.run()
