#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 root-cause-analyzer.py - 5Why 根因分析系统
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib.util
import tempfile
import shutil

scripts_dir = Path(__file__).parent.parent / 'scripts'
spec = importlib.util.spec_from_file_location("root_cause_analyzer", scripts_dir / "root-cause-analyzer.py")
rca = importlib.util.module_from_spec(spec)
sys.modules['root_cause_analyzer'] = rca
spec.loader.exec_module(rca)


class TestFiveWhys(unittest.TestCase):
    """测试 5Why 链生成功能"""

    def test_five_whys_api_error(self):
        """测试 API 错误的 5Why 链"""
        result = rca.five_whys("api_error")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertIn("为什么 API 调用失败？", result)

    def test_five_whys_config_error(self):
        """测试配置错误的 5Why 链"""
        result = rca.five_whys("config_error")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertIn("为什么配置错误？", result)

    def test_five_whys_data_error(self):
        """测试数据错误的 5Why 链"""
        result = rca.five_whys("data_error")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertIn("为什么数据格式错误？", result)

    def test_five_whys_logic_error(self):
        """测试逻辑错误的 5Why 链"""
        result = rca.five_whys("logic_error")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)

    def test_five_whys_permission_error(self):
        """测试权限错误的 5Why 链"""
        result = rca.five_whys("permission_error")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)

    def test_five_whys_unknown_category(self):
        """测试未知分类的默认 5Why 链"""
        result = rca.five_whys("unknown_category")
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertIn("为什么出现这个问题？", result)

    def test_five_whys_default(self):
        """测试默认 5Why 链"""
        result = rca.five_whys("any_category")
        default_chain = rca.five_whys("default")
        self.assertEqual(result, default_chain)


class TestParseLearning(unittest.TestCase):
    """测试学习文件解析功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_api_learning(self):
        """测试解析 API 学习文件"""
        test_file = self.temp_path / "learning-2024-01-01.md"
        content = """# API 端点调用失败
这是关于 API 调用的问题。
API HTTP 端点不正确。
"""
        test_file.write_text(content, encoding='utf-8')
        result = rca.parse_learning(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "api_error")
        self.assertIn("title", result)
        self.assertIn("content", result)

    def test_parse_config_learning(self):
        """测试解析配置学习文件"""
        test_file = self.temp_path / "learning-2024-01-02.md"
        content = """# 环境配置错误
配置文件中的环境变量未设置。
配置 config 环境变量。
"""
        test_file.write_text(content, encoding='utf-8')
        result = rca.parse_learning(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "config_error")

    def test_parse_data_learning(self):
        """测试解析数据学习文件"""
        test_file = self.temp_path / "learning-2024-01-03.md"
        content = """# JSON 数据解析失败
返回的数据格式不正确。
JSON 解析错误。
"""
        test_file.write_text(content, encoding='utf-8')
        result = rca.parse_learning(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "data_error")

    def test_parse_permission_learning(self):
        """测试解析权限学习文件"""
        test_file = self.temp_path / "learning-2024-01-04.md"
        content = """# 权限认证失败
用户权限不足，无法访问资源。
权限 授权 认证失败。
"""
        test_file.write_text(content, encoding='utf-8')
        result = rca.parse_learning(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "permission_error")

    def test_parse_unknown_learning(self):
        """测试解析未知学习文件"""
        test_file = self.temp_path / "learning-2024-01-05.md"
        content = """# 一般问题
这是一个普通的问题描述。
"""
        test_file.write_text(content, encoding='utf-8')
        result = rca.parse_learning(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result["category"], "unknown")

    def test_parse_invalid_file(self):
        """测试解析无效文件"""
        test_file = self.temp_path / "invalid.md"
        result = rca.parse_learning(test_file)
        self.assertIsNone(result)


class TestAnalyzeRootCause(unittest.TestCase):
    """测试根因分析功能"""

    def setUp(self):
        """创建测试数据"""
        self.learning = {
            "file": "test.md",
            "title": "API 调用失败",
            "category": "api_error",
            "content": """
            # API 调用失败
            根因：端点配置错误
            预防：添加配置校验
            建议：使用统一的 API 封装
            """
        }

    def test_analyze_root_cause_success(self):
        """测试根因分析成功"""
        result = rca.analyze_root_cause(self.learning)
        self.assertIsNotNone(result)
        self.assertIn("problem", result)
        self.assertIn("category", result)
        self.assertIn("why_chain", result)
        self.assertIn("root_cause", result)
        self.assertIn("preventive_actions", result)

    def test_analyze_why_chain(self):
        """测试 5Why 链生成"""
        result = rca.analyze_root_cause(self.learning)
        self.assertEqual(len(result["why_chain"]), 5)
        for i, why_item in enumerate(result["why_chain"], 1):
            self.assertEqual(why_item["level"], i)

    def test_analyze_extract_root_cause(self):
        """测试根因提取"""
        result = rca.analyze_root_cause(self.learning)
        self.assertIsNotNone(result["root_cause"])

    def test_analyze_extract_preventive_actions(self):
        """测试预防措施提取"""
        result = rca.analyze_root_cause(self.learning)
        self.assertGreater(len(result["preventive_actions"]), 0)

    def test_analyze_different_categories(self):
        """测试不同分类的根因分析"""
        categories = ["api_error", "config_error", "data_error", "logic_error", "permission_error"]
        for category in categories:
            learning = {
                "file": "test.md",
                "title": "Test",
                "category": category,
                "content": f"Content for {category}"
            }
            result = rca.analyze_root_cause(learning)
            self.assertIsNotNone(result)
            self.assertEqual(result["category"], category)


class TestGenerateRCAReport(unittest.TestCase):
    """测试根因分析报告生成功能"""

    def setUp(self):
        """创建测试数据"""
        self.analyses = [
            {
                "problem": "API 调用失败",
                "category": "api_error",
                "why_chain": [
                    {"level": 1, "why": "为什么 API 调用失败？", "answer": None},
                    {"level": 2, "why": "为什么端点错误？", "answer": None},
                    {"level": 3, "why": "为什么没有校验？", "answer": None},
                ],
                "root_cause": "端点配置错误",
                "preventive_actions": ["添加配置校验"]
            },
            {
                "problem": "配置错误",
                "category": "config_error",
                "why_chain": [
                    {"level": 1, "why": "为什么配置错误？", "answer": None},
                ],
                "root_cause": "环境变量未设置",
                "preventive_actions": ["检查环境变量"]
            }
        ]

    def test_generate_rca_report(self):
        """测试报告生成"""
        result = rca.generate_rca_report(self.analyses)
        self.assertIsInstance(result, str)
        self.assertIn("根因分析报告", result)
        self.assertIn("问题分类统计", result)

    def test_generate_rca_report_category_count(self):
        """测试分类统计"""
        result = rca.generate_rca_report(self.analyses)
        self.assertIn("api_error", result)
        self.assertIn("config_error", result)

    def test_generate_rca_report_detailed_analysis(self):
        """测试详细分析"""
        result = rca.generate_rca_report(self.analyses)
        self.assertIn("详细根因分析", result)
        self.assertIn("API 调用失败", result)

    def test_generate_rca_report_empty(self):
        """测试空分析报告"""
        result = rca.generate_rca_report([])
        self.assertIsInstance(result, str)
        self.assertIn("根因分析报告", result)

    def test_generate_rca_report_systematic_improvements(self):
        """测试系统性改进建议"""
        many_api_errors = [
            {
                "problem": f"API 错误 {i}",
                "category": "api_error",
                "why_chain": [],
                "root_cause": "test",
                "preventive_actions": []
            }
            for i in range(3)
        ]
        result = rca.generate_rca_report(many_api_errors)
        self.assertIn("系统性改进建议", result)
        self.assertIn("API 错误频发", result)


class TestWhyTemplates(unittest.TestCase):
    """测试 Why 模板定义"""

    def test_templates_defined(self):
        """测试模板定义"""
        self.assertIsInstance(rca.WHY_TEMPLATES, dict)
        self.assertIn("api_error", rca.WHY_TEMPLATES)
        self.assertIn("config_error", rca.WHY_TEMPLATES)
        self.assertIn("data_error", rca.WHY_TEMPLATES)
        self.assertIn("logic_error", rca.WHY_TEMPLATES)
        self.assertIn("permission_error", rca.WHY_TEMPLATES)
        self.assertIn("default", rca.WHY_TEMPLATES)

    def test_templates_length(self):
        """测试模板长度"""
        for category, questions in rca.WHY_TEMPLATES.items():
            self.assertEqual(len(questions), 5)


class TestCategoryPatterns(unittest.TestCase):
    """测试分类模式"""

    def setUp(self):
        """创建测试文件"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_api_category_keywords(self):
        """测试 API 分类关键词"""
        keywords = ["API", "接口", "端点", "HTTP"]
        for kw in keywords:
            test_file = self.temp_path / "test.md"
            test_file.write_text(f"Test with {kw}", encoding='utf-8')
            result = rca.parse_learning(test_file)
            self.assertEqual(result["category"], "api_error")

    def test_config_category_keywords(self):
        """测试配置分类关键词"""
        keywords = ["配置", "config", "环境变量"]
        for kw in keywords:
            test_file = self.temp_path / "test.md"
            test_file.write_text(f"Test with {kw}", encoding='utf-8')
            result = rca.parse_learning(test_file)
            self.assertEqual(result["category"], "config_error")

    def test_data_category_keywords(self):
        """测试数据分类关键词"""
        keywords = ["数据", "格式", "解析", "JSON"]
        for kw in keywords:
            test_file = self.temp_path / "test.md"
            test_file.write_text(f"Test with {kw}", encoding='utf-8')
            result = rca.parse_learning(test_file)
            self.assertEqual(result["category"], "data_error")


if __name__ == '__main__':
    unittest.main()
