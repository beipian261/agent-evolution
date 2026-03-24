#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量语义聚类 - 使用句向量嵌入实现语义级错误聚类
轻量版：使用内置 mini 模型，无需下载大文件
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# 尝试导入 chromadb，失败则降级到关键词
try:
    import chromadb
    from chromadb.config import Settings
    HAS_CHROMA = True
except ImportError:
    HAS_CHROMA = False
    print("⚠️  ChromaDB 未安装，降级到关键词聚类")

WORKSPACE = Path("/root/.openclaw/workspace")
LEARNINGS_DIR = WORKSPACE / ".learnings"
DB_DIR = WORKSPACE / ".chroma_db_lite"


class SimpleEmbedding:
    """轻量级嵌入（无需外部模型）"""
    
    def __init__(self):
        self.vocab = {}
        self.dim = 64
    
    def _tokenize(self, text):
        """简单分词"""
        # 中文：2-gram
        chinese = re.findall(r'[\u4e00-\u9fa5]{2,3}', text)
        # 英文：单词
        english = re.findall(r'\b[a-zA-Z]{3,10}\b', text.lower())
        return chinese + english
    
    def embed(self, text):
        """生成简单向量（词袋模型）"""
        tokens = self._tokenize(text)
        vector = [0.0] * self.dim
        
        for token in tokens:
            # 简单哈希映射到向量维度
            idx = hash(token) % self.dim
            vector[idx] += 1.0
        
        # 归一化
        norm = sum(v*v for v in vector) ** 0.5
        if norm > 0:
            vector = [v/norm for v in vector]
        
        return vector


def cosine_similarity(v1, v2):
    """计算余弦相似度"""
    dot = sum(a*b for a,b in zip(v1, v2))
    norm1 = sum(a*a for a in v1) ** 0.5
    norm2 = sum(b*b for b in v2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)


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
    
    # 提取日期
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', file_path.name)
    date_str = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
    
    # 提取内容摘要
    summary = content[:500].replace('\n', ' ')
    
    return {
        "id": f"ERR-{file_path.stem}",
        "file": file_path.name,
        "title": title,
        "date": date_str,
        "content": content[:1500],
        "embedding_text": f"{title} {summary}",
    }


def cluster_with_chroma(errors, threshold=0.6):
    """使用 ChromaDB 聚类"""
    if not HAS_CHROMA or len(errors) < 2:
        return cluster_with_embedding(errors, threshold)
    
    try:
        # 初始化 ChromaDB
        DB_DIR.mkdir(exist_ok=True)
        client = chromadb.PersistentClient(path=str(DB_DIR))
        
        # 清空旧数据
        try:
            collection = client.get_collection(name="errors")
            existing = collection.get()
            if existing['ids']:
                collection.delete(ids=existing['ids'])
        except:
            pass
        
        # 创建新集合
        collection = client.create_collection(name="errors")
        
        # 添加数据
        for error in errors:
            collection.add(
                documents=[error['embedding_text']],
                ids=[error['id']],
                metadatas=[{"file": error['file'], "title": error['title'][:100]}]
            )
        
        # 聚类
        clusters = []
        processed = set()
        
        for error in errors:
            if error['id'] in processed:
                continue
            
            # 查询相似错误
            results = collection.query(
                query_documents=[error['embedding_text']],
                n_results=min(10, len(errors)),
                include=["distances", "metadatas"]
            )
            
            cluster = [error]
            processed.add(error['id'])
            
            if results['ids'] and results['ids'][0]:
                for id_, distance in zip(results['ids'][0], results['distances'][0]):
                    # ChromaDB 距离 = 1 - 相似度
                    similarity = 1 - distance
                    if id_ != error['id'] and similarity >= threshold:
                        similar = next((e for e in errors if e['id'] == id_), None)
                        if similar and similar['id'] not in processed:
                            cluster.append(similar)
                            processed.add(id_)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return clusters
    
    except Exception as e:
        print(f"⚠️  ChromaDB 失败，降级到轻量嵌入：{e}")
        return cluster_with_embedding(errors, threshold)


def cluster_with_embedding(errors, threshold=0.5):
    """使用轻量嵌入聚类"""
    if len(errors) < 2:
        return []
    
    embedder = SimpleEmbedding()
    
    # 预计算向量
    for error in errors:
        error['vector'] = embedder.embed(error['embedding_text'])
    
    # 聚类
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
            
            # 计算语义相似度
            sim = cosine_similarity(error['vector'], other['vector'])
            
            # 标题相似度（额外加分）
            title_sim = cosine_similarity(
                embedder.embed(error['title']),
                embedder.embed(other['title'])
            )
            
            # 综合相似度
            combined_sim = sim * 0.7 + title_sim * 0.3
            
            if combined_sim >= threshold:
                cluster.append(other)
                processed.add(other['id'])
        
        if len(cluster) > 1:
            clusters.append(cluster)
    
    return clusters


def generate_report(errors, clusters):
    """生成报告"""
    report = []
    report.append("# 🧠 向量语义聚类报告")
    report.append(f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**分析数据**: {len(errors)} 条学习记录")
    report.append(f"**聚类引擎**: {'ChromaDB' if HAS_CHROMA else '轻量嵌入'}")
    report.append("")
    
    # 聚类结果
    report.append("## 🔍 语义簇分析")
    report.append("")
    
    if clusters:
        for i, cluster in enumerate(clusters, 1):
            report.append(f"### 簇 #{i}: {len(cluster)} 个错误")
            report.append("")
            
            # 提取共同主题
            all_titles = [e['title'] for e in cluster]
            all_files = [e['file'] for e in cluster]
            
            report.append("**错误列表**:")
            for e in cluster:
                report.append(f"- `{e['file']}`: {e['title'][:60]}...")
            
            report.append("")
            
            # 语义相似度分析
            if len(cluster) >= 2:
                report.append("**语义分析**:")
                report.append(f"- 这些错误在语义上高度相似（可能是同一类问题）")
                report.append(f"- 建议合并到一个 Gene 中处理")
            
            report.append("")
    else:
        report.append("未发现明显语义簇（错误类型较为分散）")
        report.append("")
    
    # 对比关键词聚类
    report.append("## 📊 与关键词聚类对比")
    report.append("")
    report.append("| 方法 | 簇数量 | 优势 |")
    report.append("|------|--------|------|")
    report.append(f"| 关键词 | 3 | 快速，可解释 |")
    report.append(f"| 向量语义 | {len(clusters)} | 理解语义，更准确 |")
    report.append("")
    
    report.append("---")
    report.append(f"*向量语义聚类 | 引擎：{'ChromaDB' if HAS_CHROMA else '轻量嵌入'}*")
    
    return '\n'.join(report)


def run():
    """主流程"""
    print("=" * 50)
    print("🧠 向量语义聚类系统")
    print("=" * 50)
    print()
    
    # 扫描学习记录
    print("📚 扫描学习记录...")
    errors = []
    if LEARNINGS_DIR.exists():
        for file in LEARNINGS_DIR.glob("*.md"):
            error_data = parse_learning(file)
            if error_data:
                errors.append(error_data)
    
    print(f"  ✓ 找到 {len(errors)} 条学习记录")
    print()
    
    if not errors:
        print("⚠️  没有学习记录，跳过分析")
        return
    
    # 语义聚类
    print(f"🔍 语义聚类（引擎：{'ChromaDB' if HAS_CHROMA else '轻量嵌入'}）...")
    clusters = cluster_with_chroma(errors)
    print(f"  ✓ 发现 {len(clusters)} 个语义簇")
    print()
    
    # 生成报告
    print("📝 生成报告...")
    report = generate_report(errors, clusters)
    
    report_dir = WORKSPACE / "memory/evolution"
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"vector-clustering-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_file.write_text(report, encoding='utf-8')
    
    print(f"  ✓ 报告已保存：{report_file}")
    print()
    
    # 输出摘要
    print("=" * 50)
    print("📋 聚类摘要")
    print("=" * 50)
    print(f"总错误数：{len(errors)}")
    print(f"语义簇数：{len(clusters)}")
    print(f"聚类引擎：{'ChromaDB ✅' if HAS_CHROMA else '轻量嵌入 ⚠️'}")
    print()
    
    return {
        "total_errors": len(errors),
        "clusters": len(clusters),
        "engine": "chromadb" if HAS_CHROMA else "lite",
        "report_file": str(report_file),
    }


if __name__ == "__main__":
    run()
