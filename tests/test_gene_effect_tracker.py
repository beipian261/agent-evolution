#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 gene-effect-tracker.py - Gene 效果追踪系统
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
import importlib.util
import tempfile
import shutil

scripts_dir = Path(__file__).parent.parent / 'scripts'
spec = importlib.util.spec_from_file_location("gene_effect_tracker", scripts_dir / "gene-effect-tracker.py")
get = importlib.util.module_from_spec(spec)
sys.modules['gene_effect_tracker'] = get
spec.loader.exec_module(get)


class TestLoadTrackingData(unittest.TestCase):
    """测试追踪数据加载功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_tracking_file = Path(self.test_dir) / "gene-tracking.json"

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('gene_effect_tracker.TRACKING_FILE')
    def test_load_existing_tracking_data(self, mock_file):
        """测试加载已存在的追踪数据"""
        mock_file = self.temp_tracking_file
        test_data = {
            "genes": {"gene-001": {"create_date": "2024-01-01"}},
            "last_updated": "2024-01-15"
        }
        mock_file.write_text(json.dumps(test_data), encoding='utf-8')

        with patch('gene_effect_tracker.TRACKING_FILE', mock_file):
            result = get.load_tracking_data()
            self.assertEqual(len(result['genes']), 1)
            self.assertIn("gene-001", result['genes'])

    @patch('gene_effect_tracker.TRACKING_FILE')
    def test_load_nonexistent_tracking_data(self, mock_file):
        """测试加载不存在的追踪数据"""
        mock_file = Path(self.test_dir) / "nonexistent.json"

        with patch('gene_effect_tracker.TRACKING_FILE', mock_file):
            mock_file = self.temp_tracking_file
            result = get.load_tracking_data()
            self.assertIn('genes', result)
            self.assertEqual(result['genes'], {})


class TestSaveTrackingData(unittest.TestCase):
    """测试追踪数据保存功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_tracking_file = Path(self.test_dir) / "gene-tracking.json"

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_tracking_data(self):
        """测试保存追踪数据"""
        test_data = {
            "genes": {"gene-001": {"create_date": "2024-01-01"}}
        }

        with patch('gene_effect_tracker.TRACKING_FILE', self.temp_tracking_file):
            get.save_tracking_data(test_data)
            self.assertTrue(self.temp_tracking_file.exists())

            with open(self.temp_tracking_file, 'r', encoding='utf-8') as f:
                saved_data = json.load(f)
                self.assertIn('genes', saved_data)
                self.assertIn('last_updated', saved_data)


class TestExtractGeneKeywords(unittest.TestCase):
    """测试 Gene 关键词提取功能"""

    def test_extract_api_keywords(self):
        """测试提取 API 相关关键词"""
        content = "This is an API call with HTTP endpoint"
        result = get.extract_gene_keywords(content)
        self.assertIsInstance(result, list)

    def test_extract_config_keywords(self):
        """测试提取配置相关关键词"""
        content = "Configuration error with API key"
        result = get.extract_gene_keywords(content)
        self.assertIsInstance(result, list)

    def test_extract_empty_content(self):
        """测试空内容"""
        content = ""
        result = get.extract_gene_keywords(content)
        self.assertEqual(result, [])


class TestScanGenes(unittest.TestCase):
    """测试 Gene 扫描功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_patterns_dir = Path(self.test_dir) / "patterns"
        self.temp_patterns_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scan_genes_empty_dir(self):
        """测试扫描空目录"""
        with patch('gene_effect_tracker.PATTERNS_DIR', self.temp_patterns_dir):
            result = get.scan_genes()
            self.assertEqual(result, [])

    def test_scan_genes_with_files(self):
        """测试扫描包含文件的目录"""
        gene_file = self.temp_patterns_dir / "gene-api-001.md"
        content = """# Gene API-001
**创建时间**: 2024-01-01
**触发条件**: API 调用错误
API HTTP JSON endpoint
"""
        gene_file.write_text(content, encoding='utf-8')

        with patch('gene_effect_tracker.PATTERNS_DIR', self.temp_patterns_dir):
            result = get.scan_genes()
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]['gene_id'], 'gene-api-001')


class TestScanLearnings(unittest.TestCase):
    """测试学习记录扫描功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_learnings_dir = Path(self.test_dir) / "learnings"
        self.temp_learnings_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_scan_learnings_empty_dir(self):
        """测试扫描空目录"""
        with patch('gene_effect_tracker.LEARNINGS_DIR', self.temp_learnings_dir):
            result = get.scan_learnings()
            self.assertEqual(result, [])

    def test_scan_learnings_with_files(self):
        """测试扫描包含文件的目录"""
        learning_file = self.temp_learnings_dir / "learning-2024-01-01.md"
        content = """# API 错误修复
这是关于 API 调用的问题
"""
        learning_file.write_text(content, encoding='utf-8')

        with patch('gene_effect_tracker.LEARNINGS_DIR', self.temp_learnings_dir):
            result = get.scan_learnings()
            self.assertEqual(len(result), 1)


class TestCalculateGeneEffectiveness(unittest.TestCase):
    """测试 Gene 效果计算功能"""

    def setUp(self):
        """创建测试数据"""
        self.gene = {
            "gene_id": "gene-api-001",
            "create_date": "2024-01-08",
            "keywords": ["api", "http"]
        }
        self.learnings = [
            {
                "file": "test1.md",
                "date": "2024-01-01",
                "keywords": ["api", "配置"]
            },
            {
                "file": "test2.md",
                "date": "2024-01-15",
                "keywords": ["api", "端点"]
            },
        ]

    def test_calculate_effectiveness_new_gene(self):
        """测试新 Gene 效果计算"""
        gene = {
            "gene_id": "gene-new",
            "create_date": "2024-01-08",
            "keywords": []
        }
        result = get.calculate_gene_effectiveness(gene, self.learnings)
        self.assertIsNone(result)

    def test_calculate_effectiveness_with_data(self):
        """测试有数据的 Gene 效果计算"""
        result = get.calculate_gene_effectiveness(self.gene, self.learnings)
        self.assertIsNotNone(result)
        self.assertIn("errors_before", result)
        self.assertIn("errors_after", result)
        self.assertIn("effectiveness", result)

    def test_calculate_effectiveness_reduction(self):
        """测试错误率下降"""
        learnings = [
            {"file": "test1.md", "date": "2024-01-01", "keywords": ["api"]},
            {"file": "test2.md", "date": "2024-01-02", "keywords": ["api"]},
            {"file": "test3.md", "date": "2024-01-03", "keywords": ["api"]},
            {"file": "test4.md", "date": "2024-01-10", "keywords": ["api"]},
        ]
        result = get.calculate_gene_effectiveness(self.gene, learnings)
        self.assertIsNotNone(result)


class TestGenerateReport(unittest.TestCase):
    """测试报告生成功能"""

    def setUp(self):
        """创建测试数据"""
        self.tracking_data = {
            "genes": {
                "gene-001": {
                    "create_date": "2024-01-01",
                    "errors_before": 5,
                    "errors_after": 2,
                    "reduction_rate": 60,
                    "effectiveness": "highly_effective"
                },
                "gene-002": {
                    "create_date": "2024-01-01",
                    "errors_before": 3,
                    "errors_after": 3,
                    "reduction_rate": 0,
                    "effectiveness": "no_change"
                }
            },
            "last_updated": "2024-01-15"
        }

    def test_generate_report(self):
        """测试报告生成"""
        result = get.generate_report(self.tracking_data)
        self.assertIsInstance(result, str)
        self.assertIn("Gene 效果追踪报告", result)
        self.assertIn("高效 Gene", result)
        self.assertIn("需要改进的 Gene", result)

    def test_generate_report_empty(self):
        """测试空数据报告"""
        empty_data = {"genes": {}, "last_updated": None}
        result = get.generate_report(empty_data)
        self.assertIsInstance(result, str)
        self.assertIn("暂无", result)

    def test_generate_report_classification(self):
        """测试报告分类统计"""
        result = get.generate_report(self.tracking_data)
        self.assertIn("高效 Gene", result)  # 报告使用中文标签
        self.assertIn("需要改进", result)  # 验证报告包含不同分类


class TestConstants(unittest.TestCase):
    """测试常量定义"""

    def test_workspace_defined(self):
        """测试工作空间路径定义"""
        self.assertIsInstance(get.WORKSPACE, Path)

    def test_tracking_file_path(self):
        """测试追踪文件路径"""
        self.assertIn("gene-tracking.json", str(get.TRACKING_FILE))


class TestGeneEffectivenessClassification(unittest.TestCase):
    """测试 Gene 效果分类功能"""

    def test_highly_effective_classification(self):
        """测试高效分类"""
        gene = {
            "gene_id": "gene-001",
            "create_date": "2024-01-22",
            "keywords": ["api"]
        }
        # 创建前7天：2024-01-08 到 2024-01-14（在 before_start 之前）
        learnings_before = [
            {"file": f"before{i}.md", "date": f"2024-01-{i:02d}", "keywords": ["api"]}
            for i in range(8, 15)  # 08-14, 共7个
        ]
        # 创建后只有1个：2024-01-22
        learnings_after = [
            {"file": "after22.md", "date": "2024-01-22", "keywords": ["api"]}
        ]
        learnings = learnings_before + learnings_after
        result = get.calculate_gene_effectiveness(gene, learnings)
        self.assertIsNotNone(result)
        # 预期结果：创建前7个，创建后1个，错误率下降 85.7% (> 50%)
        self.assertEqual(result['effectiveness'], 'highly_effective')
        self.assertEqual(result['errors_before'], 7)
        self.assertEqual(result['errors_after'], 1)
        self.assertGreater(result['reduction_rate'], 50)

    def test_negative_effectiveness(self):
        """测试负面效果"""
        gene = {
            "gene_id": "gene-001",
            "create_date": "2024-01-08",
            "keywords": ["api"]
        }
        learnings_before = [
            {"file": f"before{i}.md", "date": f"2024-01-0{i}", "keywords": ["api"]}
            for i in range(1, 3)
        ]
        learnings_after = [
            {"file": f"after{i}.md", "date": f"2024-01-1{i}", "keywords": ["api"]}
            for i in range(1, 8)
        ]
        learnings = learnings_before + learnings_after
        result = get.calculate_gene_effectiveness(gene, learnings)
        self.assertIsNotNone(result)


if __name__ == '__main__':
    unittest.main()
