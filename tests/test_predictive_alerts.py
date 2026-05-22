#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 predictive-alerts.py - 预测性告警系统
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
from collections import defaultdict
import importlib.util
import tempfile
import shutil

scripts_dir = Path(__file__).parent.parent / 'scripts'
spec = importlib.util.spec_from_file_location("predictive_alerts", scripts_dir / "predictive-alerts.py")
pa = importlib.util.module_from_spec(spec)
sys.modules['predictive_alerts'] = pa
spec.loader.exec_module(pa)


class TestParseLearningDate(unittest.TestCase):
    """测试学习文件日期解析功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_valid_date(self):
        """测试解析有效日期"""
        test_file = self.temp_path / "learning-2024-01-15.md"
        test_file.write_text("# Test", encoding='utf-8')
        result = pa.parse_learning_date(test_file)
        self.assertIsNotNone(result)
        self.assertEqual(result.year, 2024)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 15)

    def test_parse_invalid_date(self):
        """测试解析无效日期"""
        test_file = self.temp_path / "learning-invalid.md"
        test_file.write_text("# Test", encoding='utf-8')
        result = pa.parse_learning_date(test_file)
        self.assertIsNotNone(result)


class TestCategorizeError(unittest.TestCase):
    """测试错误分类功能"""

    def test_categorize_api_error(self):
        """测试 API 错误分类"""
        content = "API 端点调用失败，HTTP 请求错误"
        result = pa.categorize_error(content)
        self.assertEqual(result, "api_error")

    def test_categorize_config_error(self):
        """测试配置错误分类"""
        content = "配置文件错误，环境变量未设置"
        result = pa.categorize_error(content)
        self.assertEqual(result, "config_error")

    def test_categorize_data_error(self):
        """测试数据错误分类"""
        content = "JSON 数据解析失败，数据格式不正确"
        result = pa.categorize_error(content)
        self.assertEqual(result, "data_error")

    def test_categorize_other(self):
        """测试其他错误分类"""
        content = "这是一个普通的问题描述"
        result = pa.categorize_error(content)
        self.assertEqual(result, "other")

    def test_categorize_case_insensitive(self):
        """测试大小写不敏感"""
        content = "API ERROR"
        result = pa.categorize_error(content)
        self.assertEqual(result, "api_error")


class TestCollectTimeSeries(unittest.TestCase):
    """测试时间序列收集功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_learnings_dir = Path(self.test_dir) / "learnings"
        self.temp_learnings_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('predictive_alerts.LEARNINGS_DIR')
    def test_collect_time_series(self, mock_dir):
        """测试收集时间序列"""
        mock_dir = self.temp_learnings_dir
        test_file1 = self.temp_learnings_dir / "learning-2024-01-01.md"
        test_file1.write_text("API 端点错误", encoding='utf-8')
        test_file2 = self.temp_learnings_dir / "learning-2024-01-02.md"
        test_file2.write_text("配置错误", encoding='utf-8')

        with patch('predictive_alerts.LEARNINGS_DIR', self.temp_learnings_dir):
            result = pa.collect_time_series()
            self.assertIsInstance(result, defaultdict)
            self.assertIn("2024-01-01", result)
            self.assertIn("2024-01-02", result)

    @patch('predictive_alerts.LEARNINGS_DIR')
    def test_collect_empty_directory(self, mock_dir):
        """测试空目录收集"""
        mock_dir = self.temp_learnings_dir

        with patch('predictive_alerts.LEARNINGS_DIR', self.temp_learnings_dir):
            result = pa.collect_time_series()
            self.assertEqual(len(result), 0)


class TestSimpleLinearRegression(unittest.TestCase):
    """测试简单线性回归功能"""

    def test_regression_positive_slope(self):
        """测试正斜率"""
        dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
        values = [1, 2, 3]
        result = pa.simple_linear_regression(dates, values)
        self.assertIsNotNone(result)
        self.assertEqual(result["trend"], "上升")
        self.assertIn("severity", result)

    def test_regression_negative_slope(self):
        """测试负斜率"""
        dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
        values = [3, 2, 1]
        result = pa.simple_linear_regression(dates, values)
        self.assertIsNotNone(result)
        self.assertEqual(result["trend"], "下降")
        self.assertIn("severity", result)

    def test_regression_stable(self):
        """测试稳定趋势"""
        dates = ["2024-01-01", "2024-01-02", "2024-01-03"]
        values = [1, 1, 1]
        result = pa.simple_linear_regression(dates, values)
        self.assertIsNotNone(result)
        self.assertEqual(result["trend"], "平稳")
        self.assertIn("severity", result)

    def test_regression_insufficient_data(self):
        """测试数据不足"""
        dates = ["2024-01-01"]
        values = [1]
        result = pa.simple_linear_regression(dates, values)
        self.assertIsNone(result)


class TestGenerateAlerts(unittest.TestCase):
    """测试告警生成功能"""

    def test_generate_alerts_with_data(self):
        """测试有数据的告警生成"""
        daily_counts = {
            "2024-01-01": {"total": 3, "api_error": 2},
            "2024-01-02": {"total": 4, "api_error": 3},
            "2024-01-03": {"total": 5, "api_error": 4},
            "2024-01-04": {"total": 6, "api_error": 5},
        }
        result = pa.generate_alerts(daily_counts)
        self.assertIsInstance(result, list)

    def test_generate_alerts_insufficient_data(self):
        """测试数据不足的告警生成"""
        daily_counts = {
            "2024-01-01": {"total": 1},
            "2024-01-02": {"total": 2},
        }
        result = pa.generate_alerts(daily_counts)
        self.assertIsInstance(result, list)

    def test_generate_alerts_empty(self):
        """测试空数据的告警生成"""
        result = pa.generate_alerts({})
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)


class TestGenerateReport(unittest.TestCase):
    """测试报告生成功能"""

    def test_generate_report_with_alerts(self):
        """测试带告警的报告"""
        alerts = [
            {
                "category": "api_error",
                "trend": "上升",
                "severity": "🟠",
                "current": 5,
                "predicted": 8,
                "message": "API Error: 当前 5/天 → 预测 8/天"
            }
        ]
        daily_counts = {"2024-01-01": {"total": 1}}
        result = pa.generate_report(alerts, daily_counts)
        self.assertIsInstance(result, str)
        self.assertIn("预测性告警报告", result)
        self.assertIn("告警摘要", result)
        self.assertIn("API Error", result)

    def test_generate_report_without_alerts(self):
        """测试无告警的报告"""
        alerts = []
        daily_counts = {"2024-01-01": {"total": 1}}
        result = pa.generate_report(alerts, daily_counts)
        self.assertIsInstance(result, str)
        self.assertIn("预测性告警报告", result)
        self.assertIn("无异常告警", result)

    def test_generate_report_with_trend_analysis(self):
        """测试带趋势分析的报告"""
        alerts = []
        daily_counts = {
            "2024-01-01": {"total": 3, "api_error": 2},
            "2024-01-02": {"total": 4, "api_error": 3},
            "2024-01-03": {"total": 5, "api_error": 4},
            "2024-01-04": {"total": 6, "api_error": 5},
        }
        result = pa.generate_report(alerts, daily_counts)
        self.assertIn("详细趋势分析", result)


class TestConstants(unittest.TestCase):
    """测试常量定义"""

    def test_workspace_defined(self):
        """测试工作空间路径定义"""
        self.assertIsInstance(pa.WORKSPACE, Path)

    def test_learnings_dir_defined(self):
        """测试学习目录定义"""
        self.assertIsInstance(pa.LEARNINGS_DIR, Path)

    def test_alerts_dir_defined(self):
        """测试告警目录定义"""
        self.assertIsInstance(pa.ALERTS_DIR, Path)

    def test_has_prophet_defined(self):
        """测试 Prophet 标志定义"""
        self.assertIn("HAS_PROPHET", dir(pa))


class TestTimeSeriesAnalysis(unittest.TestCase):
    """测试时间序列分析功能"""

    def test_daily_counts_structure(self):
        """测试日统计结构"""
        daily_counts = {
            "2024-01-01": {"total": 3, "api_error": 2, "config_error": 1},
            "2024-01-02": {"total": 5, "api_error": 3, "data_error": 2},
        }

        self.assertIn("2024-01-01", daily_counts)
        self.assertIn("total", daily_counts["2024-01-01"])

    def test_category_counts(self):
        """测试分类统计"""
        daily_counts = {
            "2024-01-01": {"total": 3, "api_error": 2, "config_error": 1},
        }
        values = [daily_counts["2024-01-01"].get("api_error", 0)]
        self.assertEqual(values[0], 2)


class TestAlertSeverity(unittest.TestCase):
    """测试告警严重度"""

    def test_severity_high(self):
        """测试高级别告警"""
        alerts = [
            {
                "category": "total",
                "trend": "上升",
                "severity": "🟠",
                "current": 10,
                "predicted": 15,
                "message": "test"
            }
        ]
        daily_counts = {"2024-01-01": {"total": 10}}
        result = pa.generate_report(alerts, daily_counts)
        self.assertIn("🟠", result)

    def test_severity_medium(self):
        """测试中级别告警"""
        alerts = [
            {
                "category": "total",
                "trend": "小幅上升",
                "severity": "🟡",
                "current": 5,
                "predicted": 6,
                "message": "test"
            }
        ]
        daily_counts = {"2024-01-01": {"total": 5}}
        result = pa.generate_report(alerts, daily_counts)
        self.assertIn("🟡", result)

    def test_severity_low(self):
        """测试低级别告警"""
        alerts = [
            {
                "category": "total",
                "trend": "下降",
                "severity": "🟢",
                "current": 3,
                "predicted": 2,
                "message": "test"
            }
        ]
        daily_counts = {"2024-01-01": {"total": 3}}
        result = pa.generate_report(alerts, daily_counts)
        self.assertIn("🟢", result)


if __name__ == '__main__':
    unittest.main()
