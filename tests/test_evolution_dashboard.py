#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 evolution-dashboard.py - 进化 Dashboard 系统
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib.util
import tempfile
import shutil

scripts_dir = Path(__file__).parent.parent / 'scripts'
spec = importlib.util.spec_from_file_location("evolution_dashboard", scripts_dir / "evolution-dashboard.py")
ed = importlib.util.module_from_spec(spec)
sys.modules['evolution_dashboard'] = ed
spec.loader.exec_module(ed)


class TestCountFiles(unittest.TestCase):
    """测试文件计数功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_dir = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_count_files_empty_directory(self):
        """测试空目录计数"""
        result = ed.count_files(self.temp_dir)
        self.assertEqual(result, 0)

    def test_count_files_with_files(self):
        """测试有文件的目录计数"""
        (self.temp_dir / "file1.md").write_text("test", encoding='utf-8')
        (self.temp_dir / "file2.md").write_text("test", encoding='utf-8')
        (self.temp_dir / "file3.txt").write_text("test", encoding='utf-8')
        result = ed.count_files(self.temp_dir, "*.md")  # 默认模式只计数 .md 文件
        self.assertEqual(result, 2)

    def test_count_files_with_pattern(self):
        """测试带模式的文件计数"""
        (self.temp_dir / "file1.md").write_text("test", encoding='utf-8')
        (self.temp_dir / "file2.md").write_text("test", encoding='utf-8')
        (self.temp_dir / "file3.txt").write_text("test", encoding='utf-8')
        result = ed.count_files(self.temp_dir, "*.md")
        self.assertEqual(result, 2)

    def test_count_files_nonexistent_directory(self):
        """测试不存在的目录"""
        nonexistent_dir = Path(self.test_dir) / "nonexistent"
        result = ed.count_files(nonexistent_dir)
        self.assertEqual(result, 0)

    def test_count_gene_files(self):
        """测试 Gene 文件计数"""
        (self.temp_dir / "gene-api-001.md").write_text("test", encoding='utf-8')
        (self.temp_dir / "gene-config-002.md").write_text("test", encoding='utf-8')
        (self.temp_dir / "report.md").write_text("test", encoding='utf-8')
        result = ed.count_files(self.temp_dir, "gene-*.md")
        self.assertEqual(result, 2)


class TestLoadJSONFile(unittest.TestCase):
    """测试 JSON 文件加载功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_load_valid_json(self):
        """测试加载有效 JSON 文件"""
        json_file = self.temp_path / "test.json"
        test_data = {"key": "value", "count": 42}
        json_file.write_text(json.dumps(test_data), encoding='utf-8')
        result = ed.load_json_file(json_file)
        self.assertEqual(result["key"], "value")
        self.assertEqual(result["count"], 42)

    def test_load_invalid_json(self):
        """测试加载无效 JSON 文件"""
        json_file = self.temp_path / "invalid.json"
        json_file.write_text("invalid json content", encoding='utf-8')
        result = ed.load_json_file(json_file)
        self.assertEqual(result, {})

    def test_load_nonexistent_json(self):
        """测试加载不存在的 JSON 文件"""
        json_file = self.temp_path / "nonexistent.json"
        result = ed.load_json_file(json_file)
        self.assertEqual(result, {})

    def test_load_empty_json(self):
        """测试加载空 JSON 文件"""
        json_file = self.temp_path / "empty.json"
        json_file.write_text("", encoding='utf-8')
        result = ed.load_json_file(json_file)
        self.assertEqual(result, {})


class TestGetLatestReportContent(unittest.TestCase):
    """测试最新报告内容获取功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_dir = Path(self.test_dir)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_latest_report(self):
        """测试获取最新报告"""
        report1 = self.temp_dir / "report-2024-01-01.md"
        report1.write_text("Report 1 content", encoding='utf-8')
        report2 = self.temp_dir / "report-2024-01-02.md"
        report2.write_text("Report 2 content", encoding='utf-8')
        result = ed.get_latest_report_content(self.temp_dir, "report-")
        self.assertIsNotNone(result)
        self.assertIn("Report 2 content", result)

    def test_get_latest_report_nonexistent_dir(self):
        """测试获取不存在的报告目录"""
        result = ed.get_latest_report_content(self.temp_dir / "nonexistent", "report-")
        self.assertIsNone(result)

    def test_get_latest_report_no_files(self):
        """测试获取无文件的报告目录"""
        result = ed.get_latest_report_content(self.temp_dir, "report-")
        self.assertIsNone(result)

    def test_get_latest_report_prefix(self):
        """测试报告前缀过滤"""
        report1 = self.temp_dir / "api-report.md"
        report1.write_text("API Report", encoding='utf-8')
        report2 = self.temp_dir / "config-report.md"
        report2.write_text("Config Report", encoding='utf-8')
        result = ed.get_latest_report_content(self.temp_dir, "api-")
        self.assertIsNotNone(result)
        self.assertIn("API Report", result)


class TestGenerateDashboard(unittest.TestCase):
    """测试 Dashboard 生成功能"""

    def setUp(self):
        """创建临时测试目录结构"""
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir)
        self.patterns_dir = self.workspace / "patterns"
        self.learnings_dir = self.workspace / "learnings"
        self.evolution_dir = self.workspace / "memory" / "evolution"
        self.rca_dir = self.evolution_dir / "rca"
        self.alerts_dir = self.evolution_dir / "alerts"
        self.scripts_dir = self.workspace / "scripts"
        self.fixes_dir = self.scripts_dir / "auto-fixes"

        for d in [self.patterns_dir, self.learnings_dir, self.evolution_dir,
                  self.rca_dir, self.alerts_dir, self.fixes_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('evolution_dashboard.WORKSPACE')
    @patch('evolution_dashboard.PATTERNS_DIR')
    @patch('evolution_dashboard.LEARNINGS_DIR')
    @patch('evolution_dashboard.EVOLUTION_DIR')
    def test_generate_dashboard(self, mock_evolution, mock_learnings,
                                 mock_patterns, mock_workspace):
        """测试 Dashboard 生成"""
        mock_workspace = self.workspace
        mock_patterns = self.patterns_dir
        mock_learnings = self.learnings_dir
        mock_evolution = self.evolution_dir

        (self.patterns_dir / "gene-api-001.md").write_text("Gene 1", encoding='utf-8')
        (self.learnings_dir / "learning-001.md").write_text("Learning 1", encoding='utf-8')
        (self.evolution_dir / "report.md").write_text("Report", encoding='utf-8')

        result = ed.generate_dashboard()
        self.assertIsInstance(result, str)
        self.assertIn("智能进化系统 Dashboard", result)
        self.assertIn("核心指标", result)

    @patch('evolution_dashboard.WORKSPACE')
    @patch('evolution_dashboard.PATTERNS_DIR')
    @patch('evolution_dashboard.LEARNINGS_DIR')
    @patch('evolution_dashboard.EVOLUTION_DIR')
    def test_generate_dashboard_with_data(self, mock_evolution, mock_learnings,
                                           mock_patterns, mock_workspace):
        """测试带数据的 Dashboard 生成"""
        mock_workspace = self.workspace
        mock_patterns = self.patterns_dir
        mock_learnings = self.learnings_dir
        mock_evolution = self.evolution_dir

        for i in range(3):
            (self.patterns_dir / f"gene-api-{i:03d}.md").write_text("Gene", encoding='utf-8')
        for i in range(5):
            (self.learnings_dir / f"learning-{i:03d}.md").write_text("Learning", encoding='utf-8')

        tracking_file = self.evolution_dir / "gene-tracking.json"
        tracking_file.write_text(json.dumps({"genes": {"g1": {}, "g2": {}}}), encoding='utf-8')

        result = ed.generate_dashboard()
        self.assertIn("3", result)


class TestDashboardContent(unittest.TestCase):
    """测试 Dashboard 内容"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir)
        self.patterns_dir = self.workspace / "patterns"
        self.learnings_dir = self.workspace / "learnings"
        self.evolution_dir = self.workspace / "memory" / "evolution"
        self.rca_dir = self.evolution_dir / "rca"
        self.alerts_dir = self.evolution_dir / "alerts"
        self.scripts_dir = self.workspace / "scripts"
        self.fixes_dir = self.scripts_dir / "auto-fixes"

        for d in [self.patterns_dir, self.learnings_dir, self.evolution_dir,
                  self.rca_dir, self.alerts_dir, self.fixes_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('evolution_dashboard.WORKSPACE')
    @patch('evolution_dashboard.PATTERNS_DIR')
    @patch('evolution_dashboard.LEARNINGS_DIR')
    @patch('evolution_dashboard.EVOLUTION_DIR')
    def test_dashboard_contains_metrics(self, mock_evolution, mock_learnings,
                                         mock_patterns, mock_workspace):
        """测试 Dashboard 包含指标"""
        mock_workspace = self.workspace
        mock_patterns = self.patterns_dir
        mock_learnings = self.learnings_dir
        mock_evolution = self.evolution_dir

        result = ed.generate_dashboard()
        self.assertIn("Gene 总数", result)
        self.assertIn("学习记录", result)
        self.assertIn("进化报告", result)

    @patch('evolution_dashboard.WORKSPACE')
    @patch('evolution_dashboard.PATTERNS_DIR')
    @patch('evolution_dashboard.LEARNINGS_DIR')
    @patch('evolution_dashboard.EVOLUTION_DIR')
    def test_dashboard_contains_sections(self, mock_evolution, mock_learnings,
                                           mock_patterns, mock_workspace):
        """测试 Dashboard 包含各个部分"""
        mock_workspace = self.workspace
        mock_patterns = self.patterns_dir
        mock_learnings = self.learnings_dir
        mock_evolution = self.evolution_dir

        result = ed.generate_dashboard()
        self.assertIn("核心指标", result)
        self.assertIn("最新告警", result)
        self.assertIn("系统状态", result)
        self.assertIn("快速操作", result)

    @patch('evolution_dashboard.WORKSPACE')
    @patch('evolution_dashboard.PATTERNS_DIR')
    @patch('evolution_dashboard.LEARNINGS_DIR')
    @patch('evolution_dashboard.EVOLUTION_DIR')
    def test_dashboard_timestamp(self, mock_evolution, mock_learnings,
                                  mock_patterns, mock_workspace):
        """测试 Dashboard 包含时间戳"""
        mock_workspace = self.workspace
        mock_patterns = self.patterns_dir
        mock_learnings = self.learnings_dir
        mock_evolution = self.evolution_dir

        result = ed.generate_dashboard()
        self.assertIn("生成时间", result)


class TestConstants(unittest.TestCase):
    """测试常量定义"""

    def test_workspace_defined(self):
        """测试工作空间路径定义"""
        self.assertIsInstance(ed.WORKSPACE, Path)

    def test_evolution_dir_defined(self):
        """测试进化目录定义"""
        self.assertIsInstance(ed.EVOLUTION_DIR, Path)

    def test_patterns_dir_defined(self):
        """测试模式目录定义"""
        self.assertIsInstance(ed.PATTERNS_DIR, Path)

    def test_learnings_dir_defined(self):
        """测试学习目录定义"""
        self.assertIsInstance(ed.LEARNINGS_DIR, Path)


class TestDashboardScripts(unittest.TestCase):
    """测试 Dashboard 脚本检查"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.workspace = Path(self.test_dir)
        self.scripts_dir = self.workspace / "scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('evolution_dashboard.WORKSPACE')
    def test_dashboard_checks_scripts(self, mock_workspace):
        """测试 Dashboard 检查脚本"""
        mock_workspace = self.workspace

        (self.scripts_dir / "smart-evolution-lite.py").write_text("#!/usr/bin/env python3", encoding='utf-8')

        with patch('evolution_dashboard.WORKSPACE', self.workspace):
            result = ed.generate_dashboard()
            self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
