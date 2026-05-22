#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 vector-clustering.py - 向量语义聚类系统
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib.util
import tempfile
import shutil

scripts_dir = Path(__file__).parent.parent / 'scripts'
spec = importlib.util.spec_from_file_location("vector_clustering", scripts_dir / "vector-clustering.py")
vc = importlib.util.module_from_spec(spec)
sys.modules['vector_clustering'] = vc
spec.loader.exec_module(vc)


class TestSimpleEmbedding(unittest.TestCase):
    """测试简单嵌入类"""

    def setUp(self):
        """创建嵌入实例"""
        self.embedder = vc.SimpleEmbedding()

    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.embedder.dim, 64)

    def test_tokenize_chinese(self):
        """测试中文分词"""
        text = "API错误配置问题"
        result = self.embedder._tokenize(text)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_tokenize_english(self):
        """测试英文分词"""
        text = "API configuration error handling"
        result = self.embedder._tokenize(text)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_tokenize_mixed(self):
        """测试混合分词"""
        text = "API error 错误处理 configuration 配置"
        result = self.embedder._tokenize(text)
        self.assertIsInstance(result, list)

    def test_embed_returns_vector(self):
        """测试嵌入返回向量"""
        text = "API configuration error"
        result = self.embedder.embed(text)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 64)

    def test_embed_normalized(self):
        """测试嵌入归一化"""
        text = "API error"
        vector = self.embedder.embed(text)
        norm = sum(v*v for v in vector) ** 0.5
        self.assertAlmostEqual(norm, 1.0, places=5)

    def test_embed_empty_text(self):
        """测试空文本嵌入"""
        vector = self.embedder.embed("")
        self.assertIsInstance(vector, list)
        self.assertEqual(len(vector), 64)


class TestCosineSimilarity(unittest.TestCase):
    """测试余弦相似度计算"""

    def test_identical_vectors(self):
        """测试相同向量"""
        v1 = [1.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        result = vc.cosine_similarity(v1, v2)
        self.assertEqual(result, 1.0)

    def test_perpendicular_vectors(self):
        """测试垂直向量"""
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        result = vc.cosine_similarity(v1, v2)
        self.assertEqual(result, 0.0)

    def test_opposite_vectors(self):
        """测试相反向量"""
        v1 = [1.0, 0.0, 0.0]
        v2 = [-1.0, 0.0, 0.0]
        result = vc.cosine_similarity(v1, v2)
        self.assertEqual(result, -1.0)

    def test_similar_vectors(self):
        """测试相似向量"""
        v1 = [1.0, 2.0, 3.0]
        v2 = [1.1, 2.1, 3.1]
        result = vc.cosine_similarity(v1, v2)
        self.assertGreater(result, 0.9)

    def test_zero_vector(self):
        """测试零向量"""
        v1 = [0.0, 0.0, 0.0]
        v2 = [1.0, 0.0, 0.0]
        result = vc.cosine_similarity(v1, v2)
        self.assertEqual(result, 0.0)


class TestParseLearning(unittest.TestCase):
    """测试学习文件解析功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_learning_success(self):
        """测试成功解析"""
        test_file = self.temp_path / "learning-2024-01-01.md"
        content = """# API 端点调用失败
这是关于 API 调用失败的问题描述。
"""
        test_file.write_text(content, encoding='utf-8')
        result = vc.parse_learning(test_file)
        self.assertIsNotNone(result)
        self.assertIn("id", result)
        self.assertIn("title", result)
        self.assertIn("date", result)
        self.assertIn("content", result)
        self.assertIn("embedding_text", result)

    def test_parse_learning_extract_title(self):
        """测试提取标题"""
        test_file = self.temp_path / "learning-2024-01-02.md"
        content = """# 测试标题
这是测试内容。
"""
        test_file.write_text(content, encoding='utf-8')
        result = vc.parse_learning(test_file)
        self.assertEqual(result["title"], "测试标题")

    def test_parse_learning_extract_date(self):
        """测试提取日期"""
        test_file = self.temp_path / "learning-2024-01-15.md"
        content = """# Test
Content
"""
        test_file.write_text(content, encoding='utf-8')
        result = vc.parse_learning(test_file)
        self.assertEqual(result["date"], "2024-01-15")

    def test_parse_learning_invalid_file(self):
        """测试无效文件"""
        test_file = self.temp_path / "invalid.md"
        result = vc.parse_learning(test_file)
        self.assertIsNone(result)


class TestClusterWithEmbedding(unittest.TestCase):
    """测试轻量嵌入聚类功能"""

    def setUp(self):
        """创建测试数据"""
        self.errors = [
            {
                "id": "ERR-001",
                "file": "test1.md",
                "title": "API 调用失败",
                "date": "2024-01-01",
                "content": "API 端点配置错误",
                "embedding_text": "API 调用失败 API 端点配置错误"
            },
            {
                "id": "ERR-002",
                "file": "test2.md",
                "title": "API 配置问题",
                "date": "2024-01-02",
                "content": "API 配置不正确",
                "embedding_text": "API 配置问题 API 配置不正确"
            },
            {
                "id": "ERR-003",
                "file": "test3.md",
                "title": "数据库连接失败",
                "date": "2024-01-03",
                "content": "数据库连接超时",
                "embedding_text": "数据库连接失败 数据库连接超时"
            },
        ]

    def test_cluster_similar_errors(self):
        """测试相似错误聚类"""
        result = vc.cluster_with_embedding(self.errors, threshold=0.5)
        self.assertIsInstance(result, list)

    def test_cluster_single_error(self):
        """测试单个错误"""
        result = vc.cluster_with_embedding([self.errors[0]])
        self.assertEqual(result, [])

    def test_cluster_empty(self):
        """测试空列表"""
        result = vc.cluster_with_embedding([])
        self.assertEqual(result, [])

    def test_cluster_with_high_threshold(self):
        """测试高阈值聚类"""
        result = vc.cluster_with_embedding(self.errors, threshold=0.9)
        self.assertIsInstance(result, list)

    def test_cluster_with_low_threshold(self):
        """测试低阈值聚类"""
        result = vc.cluster_with_embedding(self.errors, threshold=0.1)
        self.assertIsInstance(result, list)


class TestClusterWithChroma(unittest.TestCase):
    """测试 ChromaDB 聚类功能"""

    def setUp(self):
        """创建测试数据"""
        self.errors = [
            {
                "id": "ERR-001",
                "file": "test1.md",
                "title": "API 调用失败",
                "date": "2024-01-01",
                "content": "API 端点配置错误",
                "embedding_text": "API 调用失败"
            },
            {
                "id": "ERR-002",
                "file": "test2.md",
                "title": "API 配置问题",
                "date": "2024-01-02",
                "content": "API 配置不正确",
                "embedding_text": "API 配置问题"
            },
        ]

    def test_cluster_fallback_to_embedding(self):
        """测试降级到轻量嵌入"""
        result = vc.cluster_with_chroma(self.errors, threshold=0.5)
        self.assertIsInstance(result, list)


class TestGenerateReport(unittest.TestCase):
    """测试报告生成功能"""

    def setUp(self):
        """创建测试数据"""
        self.errors = [
            {
                "id": "ERR-001",
                "file": "test1.md",
                "title": "API 调用失败",
                "date": "2024-01-01",
                "content": "API 端点配置错误",
                "embedding_text": "API 调用失败"
            }
        ]
        self.clusters = []

    def test_generate_report(self):
        """测试报告生成"""
        result = vc.generate_report(self.errors, self.clusters)
        self.assertIsInstance(result, str)
        self.assertIn("向量语义聚类报告", result)
        self.assertIn("分析数据", result)

    def test_generate_report_with_clusters(self):
        """测试带聚类的报告"""
        cluster = [self.errors[0]]
        self.clusters = [cluster]
        result = vc.generate_report(self.errors, self.clusters)
        self.assertIn("语义簇分析", result)

    def test_generate_report_engine_info(self):
        """测试报告包含引擎信息"""
        result = vc.generate_report(self.errors, self.clusters)
        self.assertIn("聚类引擎", result)


class TestEmbeddingText(unittest.TestCase):
    """测试嵌入文本生成"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_embedding_text_generation(self):
        """测试嵌入文本生成"""
        test_file = self.temp_path / "learning-2024-01-01.md"
        content = """# API 端点调用失败
这是关于 API 端点配置错误的详细描述。
"""
        test_file.write_text(content, encoding='utf-8')
        result = vc.parse_learning(test_file)
        self.assertIn("embedding_text", result)
        self.assertIsInstance(result["embedding_text"], str)


class TestConstants(unittest.TestCase):
    """测试常量定义"""

    def test_has_chroma_defined(self):
        """测试 ChromaDB 标志定义"""
        self.assertIn("HAS_CHROMA", dir(vc))

    def test_workspace_defined(self):
        """测试工作空间路径定义"""
        self.assertIsInstance(vc.WORKSPACE, Path)

    def test_embeddings_dir_defined(self):
        """测试嵌入目录定义"""
        self.assertIsInstance(vc.DB_DIR, Path)


if __name__ == '__main__':
    unittest.main()
