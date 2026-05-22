#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 smart-evolution-lite.py - 轻量智能进化分析系统
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from collections import Counter
import importlib.util
import tempfile
import shutil

scripts_dir = Path(__file__).parent.parent / 'scripts'
spec = importlib.util.spec_from_file_location("smart_evolution_lite", scripts_dir / "smart-evolution-lite.py")
sel = importlib.util.module_from_spec(spec)
sys.modules['smart_evolution_lite'] = sel
spec.loader.exec_module(sel)


class TestErrorClassification(unittest.TestCase):
    """测试错误分类功能"""

    def test_classify_api_error(self):
        """测试 API 错误分类"""
        content = "API 调用失败，端点不正确，HTTP 请求超时"
        result = sel.classify_error(content)
        self.assertEqual(result, "api_error")

    def test_classify_config_error(self):
        """测试配置错误分类"""
        content = "配置错误，环境变量未设置，token 过期"
        result = sel.classify_error(content)
        self.assertEqual(result, "config_error")

    def test_classify_data_error(self):
        """测试数据错误分类"""
        content = "数据格式错误，JSON 解析失败，数据库连接失败"
        result = sel.classify_error(content)
        self.assertEqual(result, "data_error")

    def test_classify_permission_error(self):
        """测试权限错误分类"""
        content = "权限不足，403 禁止访问，认证失败"
        result = sel.classify_error(content)
        self.assertEqual(result, "permission_error")

    def test_classify_network_error(self):
        """测试网络错误分类"""
        content = "网络超时，连接断开，无法连接到服务器"
        result = sel.classify_error(content)
        self.assertEqual(result, "network_error")

    def test_classify_unknown(self):
        """测试未知错误分类"""
        content = "这是一个普通的问题描述"
        result = sel.classify_error(content)
        self.assertEqual(result, "unknown")

    def test_classify_case_insensitive(self):
        """测试大小写不敏感"""
        content = "API ERROR HTTP REQUEST"
        result = sel.classify_error(content)
        self.assertEqual(result, "api_error")


class TestSeverityAssessment(unittest.TestCase):
    """测试严重度评估功能"""

    def test_assess_critical(self):
        """测试严重级别评估"""
        content = "系统崩溃，数据丢失，安全漏洞"
        result = sel.assess_severity(content)
        self.assertEqual(result, "critical")

    def test_assess_high(self):
        """测试高级别评估"""
        content = "API 调用失败，程序报错"
        result = sel.assess_severity(content)
        self.assertEqual(result, "high")

    def test_assess_medium(self):
        """测试中等级别评估"""
        content = "系统警告，性能降级"
        result = sel.assess_severity(content)
        self.assertEqual(result, "medium")

    def test_assess_low(self):
        """测试低级别评估"""
        content = "建议优化代码性能"
        result = sel.assess_severity(content)
        self.assertEqual(result, "low")

    def test_assess_default(self):
        """测试默认级别"""
        content = "这是一个普通的问题"
        result = sel.assess_severity(content)
        self.assertEqual(result, "medium")


class TestKeywordExtraction(unittest.TestCase):
    """测试关键词提取功能"""

    def test_extract_keywords_chinese(self):
        """测试中文关键词提取"""
        content = "这是一个关于API配置和JSON解析的问题描述"
        result = sel.extract_keywords(content)
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 5)

    def test_extract_keywords_english(self):
        """测试英文关键词提取"""
        content = "API error handling configuration management"
        result = sel.extract_keywords(content)
        self.assertIsInstance(result, list)

    def test_extract_keywords_empty(self):
        """测试空内容"""
        content = "the is are"
        result = sel.extract_keywords(content)
        self.assertEqual(result, [])


class TestSolutionExtraction(unittest.TestCase):
    """测试解决方案提取功能"""

    def test_extract_solution_with_keywords(self):
        """测试带关键词的解决方案提取"""
        content = """
        问题描述
        解决方案：重新配置 API 端点
        修复方法：更新 JSON 数据结构
        """
        result = sel.extract_solution(content)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_extract_solution_default(self):
        """测试默认解决方案"""
        content = "这是一个普通的问题描述"
        result = sel.extract_solution(content)
        self.assertEqual(len(result), 3)
        self.assertIn("分析错误日志", result)


class TestKeywordSimilarity(unittest.TestCase):
    """测试关键词相似度计算"""

    def test_similarity_identical(self):
        """测试完全相同的关键词"""
        kw1 = ["API", "配置", "错误"]
        kw2 = ["API", "配置", "错误"]
        result = sel.keyword_similarity(kw1, kw2)
        self.assertEqual(result, 1.0)

    def test_similarity_partial(self):
        """测试部分相同"""
        kw1 = ["API", "配置", "错误"]
        kw2 = ["API", "网络", "错误"]
        result = sel.keyword_similarity(kw1, kw2)
        self.assertGreater(result, 0.0)
        self.assertLess(result, 1.0)

    def test_similarity_none(self):
        """测试完全不同"""
        kw1 = ["API"]
        kw2 = ["数据库"]
        result = sel.keyword_similarity(kw1, kw2)
        self.assertEqual(result, 0.0)

    def test_similarity_empty(self):
        """测试空关键词"""
        result = sel.keyword_similarity([], ["API"])
        self.assertEqual(result, 0.0)


class TestErrorClustering(unittest.TestCase):
    """测试错误聚类功能"""

    def setUp(self):
        """创建测试数据"""
        self.errors = [
            {
                "id": "ERR-001",
                "category": "api_error",
                "keywords": ["API", "端点", "请求"],
                "file": "test1.md",
                "date": "2024-01-01",
                "solution": ["修复端点"]
            },
            {
                "id": "ERR-002",
                "category": "api_error",
                "keywords": ["API", "配置", "错误"],
                "file": "test2.md",
                "date": "2024-01-02",
                "solution": ["更新配置"]
            },
            {
                "id": "ERR-003",
                "category": "data_error",
                "keywords": ["JSON", "解析", "数据"],
                "file": "test3.md",
                "date": "2024-01-03",
                "solution": ["修改解析"]
            },
        ]

    def test_cluster_similar_errors(self):
        """测试相似错误聚类"""
        result = sel.cluster_errors(self.errors, similarity_threshold=0.3)
        self.assertIsInstance(result, list)

    def test_cluster_single_error(self):
        """测试单个错误"""
        result = sel.cluster_errors([self.errors[0]])
        self.assertEqual(result, [])

    def test_cluster_empty(self):
        """测试空列表"""
        result = sel.cluster_errors([])
        self.assertEqual(result, [])


class TestRootCauseAnalysis(unittest.TestCase):
    """测试根因分析功能"""

    def setUp(self):
        """创建测试簇数据"""
        self.cluster = [
            {
                "id": "ERR-001",
                "category": "api_error",
                "keywords": ["API", "端点", "请求"],
                "file": "test1.md",
                "date": "2024-01-01",
                "solution": ["修复端点"]
            },
            {
                "id": "ERR-002",
                "category": "api_error",
                "keywords": ["API", "配置", "端点"],
                "file": "test2.md",
                "date": "2024-01-02",
                "solution": ["更新配置"]
            },
        ]

    def test_analyze_root_cause(self):
        """测试根因分析"""
        result = sel.analyze_root_cause(self.cluster)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "api_error")
        self.assertEqual(result["occurrence_count"], 2)

    def test_analyze_root_cause_empty(self):
        """测试空簇"""
        result = sel.analyze_root_cause([])
        self.assertIsNone(result)


class TestGeneSuggestion(unittest.TestCase):
    """测试 Gene 建议生成功能"""

    def setUp(self):
        """创建测试根因数据"""
        self.root_cause = {
            "category": "api_error",
            "top_keywords": ["API", "端点", "配置"],
            "common_solutions": ["修复端点", "更新配置"],
            "occurrence_count": 3
        }
        self.cluster = [1, 2, 3]

    def test_generate_gene_suggestion(self):
        """测试 Gene 建议生成"""
        result = sel.generate_gene_suggestion(self.root_cause, self.cluster)
        self.assertIsNotNone(result)
        self.assertIn("gene_id", result)
        self.assertIn("name", result)
        self.assertIn("trigger", result)
        self.assertIn("confidence", result)
        self.assertEqual(result["cluster_size"], 3)


class TestReportGeneration(unittest.TestCase):
    """测试报告生成功能"""

    def setUp(self):
        """创建测试数据"""
        self.errors = [
            {
                "id": "ERR-001",
                "category": "api_error",
                "severity": "high",
                "keywords": ["API"],
                "file": "test.md",
                "date": "2024-01-01",
                "solution": []
            }
        ]
        self.clusters = []
        self.genes = []

    def test_generate_report(self):
        """测试报告生成"""
        result = sel.generate_report(self.errors, self.clusters, self.genes)
        self.assertIsInstance(result, str)
        self.assertIn("智能进化分析报告", result)
        self.assertIn("错误类型分布", result)

    def test_generate_report_with_clusters(self):
        """测试带聚类的报告"""
        self.clusters = [[self.errors[0]]]
        result = sel.generate_report(self.errors, self.clusters, self.genes)
        self.assertIn("错误簇分析", result)


class TestParseLearningFile(unittest.TestCase):
    """测试学习文件解析功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_learning_file_success(self):
        """测试成功解析"""
        test_file = self.temp_path / "learning-2024-01-01.md"
        content = """# API 错误处理
这是关于 API 调用失败的问题。
解决方案：修复端点配置。
"""
        test_file.write_text(content, encoding='utf-8')
        result = sel.parse_learning_file(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "api_error")
        self.assertIn("id", result)
        self.assertIn("title", result)

    def test_parse_learning_file_invalid(self):
        """测试无效文件"""
        test_file = self.temp_path / "test.md"
        result = sel.parse_learning_file(test_file)
        self.assertIsNone(result)


class TestConstants(unittest.TestCase):
    """测试常量定义"""

    def test_error_categories_defined(self):
        """测试错误分类定义"""
        self.assertIsInstance(sel.ERROR_CATEGORIES, dict)
        self.assertIn("api_error", sel.ERROR_CATEGORIES)
        self.assertIn("config_error", sel.ERROR_CATEGORIES)
        self.assertIn("data_error", sel.ERROR_CATEGORIES)

    def test_severity_keywords_defined(self):
        """测试严重度关键词定义"""
        self.assertIsInstance(sel.SEVERITY_KEYWORDS, dict)
        self.assertIn("critical", sel.SEVERITY_KEYWORDS)
        self.assertIn("high", sel.SEVERITY_KEYWORDS)
        self.assertIn("medium", sel.SEVERITY_KEYWORDS)
        self.assertIn("low", sel.SEVERITY_KEYWORDS)

    def test_solution_keywords_defined(self):
        """测试解决方案关键词定义"""
        self.assertIsInstance(sel.SOLUTION_KEYWORDS, list)
        self.assertGreater(len(sel.SOLUTION_KEYWORDS), 0)


if __name__ == '__main__':
    unittest.main()
