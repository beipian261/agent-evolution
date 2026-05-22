#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 auto-fix-generator.py - 自动修复生成系统
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch
import importlib.util
import tempfile
import shutil

scripts_dir = Path(__file__).parent.parent / 'scripts'
spec = importlib.util.spec_from_file_location("auto_fix_generator", scripts_dir / "auto-fix-generator.py")
afg = importlib.util.module_from_spec(spec)
sys.modules['auto_fix_generator'] = afg
spec.loader.exec_module(afg)


class TestFixTemplates(unittest.TestCase):
    """测试修复模板功能"""

    def test_get_api_fix_template(self):
        """测试 API 修复模板"""
        result = afg.get_api_fix_template()
        self.assertIsInstance(result, str)
        self.assertIn("#!/bin/bash", result)
        self.assertIn("API", result)

    def test_get_config_fix_template(self):
        """测试配置修复模板"""
        result = afg.get_config_fix_template()
        self.assertIsInstance(result, str)
        self.assertIn("#!/bin/bash", result)
        self.assertIn("配置", result)

    def test_get_data_fix_template(self):
        """测试数据修复模板"""
        result = afg.get_data_fix_template()
        self.assertIsInstance(result, str)
        self.assertIn("#!/bin/bash", result)
        self.assertIn("数据", result)

    def test_get_file_fix_template(self):
        """测试文件修复模板"""
        result = afg.get_file_fix_template()
        self.assertIsInstance(result, str)
        self.assertIn("#!/bin/bash", result)
        self.assertIn("文件", result)

    def test_get_fix_template_api(self):
        """测试获取 API 修复模板"""
        result = afg.get_fix_template("api_error")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_get_fix_template_config(self):
        """测试获取配置修复模板"""
        result = afg.get_fix_template("config_error")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_get_fix_template_data(self):
        """测试获取数据修复模板"""
        result = afg.get_fix_template("data_error")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_get_fix_template_file(self):
        """测试获取文件修复模板"""
        result = afg.get_fix_template("file_error")
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_get_fix_template_unknown(self):
        """测试获取未知模板"""
        result = afg.get_fix_template("unknown_error")
        self.assertIsNone(result)


class TestAnalyzeForFixes(unittest.TestCase):
    """测试错误分析功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_learnings_dir = Path(self.test_dir) / "learnings"
        self.temp_learnings_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('auto_fix_generator.LEARNINGS_DIR')
    def test_analyze_api_errors(self, mock_dir):
        """测试 API 错误分析"""
        mock_dir = self.temp_learnings_dir
        api_file1 = self.temp_learnings_dir / "api-error-1.md"
        api_file1.write_text("API 端点调用失败", encoding='utf-8')
        api_file2 = self.temp_learnings_dir / "api-error-2.md"
        api_file2.write_text("API 配置不正确", encoding='utf-8')

        with patch('auto_fix_generator.LEARNINGS_DIR', self.temp_learnings_dir):
            result = afg.analyze_for_fixes()
            self.assertIsInstance(result, list)

    @patch('auto_fix_generator.LEARNINGS_DIR')
    def test_analyze_config_errors(self, mock_dir):
        """测试配置错误分析"""
        mock_dir = self.temp_learnings_dir
        config_file1 = self.temp_learnings_dir / "config-error-1.md"
        config_file1.write_text("配置文件错误", encoding='utf-8')
        config_file2 = self.temp_learnings_dir / "config-error-2.md"
        config_file2.write_text("环境变量配置失败", encoding='utf-8')

        with patch('auto_fix_generator.LEARNINGS_DIR', self.temp_learnings_dir):
            result = afg.analyze_for_fixes()
            self.assertIsInstance(result, list)

    @patch('auto_fix_generator.LEARNINGS_DIR')
    def test_analyze_data_errors(self, mock_dir):
        """测试数据错误分析"""
        mock_dir = self.temp_learnings_dir
        data_file1 = self.temp_learnings_dir / "data-error-1.md"
        data_file1.write_text("JSON 解析失败", encoding='utf-8')
        data_file2 = self.temp_learnings_dir / "data-error-2.md"
        data_file2.write_text("数据格式错误", encoding='utf-8')

        with patch('auto_fix_generator.LEARNINGS_DIR', self.temp_learnings_dir):
            result = afg.analyze_for_fixes()
            self.assertIsInstance(result, list)

    @patch('auto_fix_generator.LEARNINGS_DIR')
    def test_analyze_empty_directory(self, mock_dir):
        """测试空目录分析"""
        mock_dir = self.temp_learnings_dir

        with patch('auto_fix_generator.LEARNINGS_DIR', self.temp_learnings_dir):
            result = afg.analyze_for_fixes()
            self.assertEqual(result, [])

    @patch('auto_fix_generator.LEARNINGS_DIR')
    def test_analyze_threshold(self, mock_dir):
        """测试分析阈值"""
        mock_dir = self.temp_learnings_dir
        single_file = self.temp_learnings_dir / "api-error-1.md"
        single_file.write_text("API 错误", encoding='utf-8')

        with patch('auto_fix_generator.LEARNINGS_DIR', self.temp_learnings_dir):
            result = afg.analyze_for_fixes()
            api_fixes = [f for f in result if f["category"] == "api_error"]
            self.assertEqual(len(api_fixes), 0)


class TestSaveFixScript(unittest.TestCase):
    """测试修复脚本保存功能"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_fixes_dir = Path(self.test_dir) / "auto-fixes"
        self.temp_fixes_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_save_fix_script(self):
        """测试保存修复脚本"""
        fix = {
            "category": "api_error",
            "name": "API 修复",
            "count": 2,
            "script": "#!/bin/bash\necho 'Test'"
        }

        with patch('auto_fix_generator.FIXES_DIR', self.temp_fixes_dir):
            result = afg.save_fix_script(fix)
            self.assertIsInstance(result, str)
            script_file = Path(result)
            self.assertTrue(script_file.exists())

    def test_save_fix_script_content(self):
        """测试保存脚本内容"""
        fix = {
            "category": "config_error",
            "name": "配置修复",
            "count": 2,
            "script": "#!/bin/bash\necho 'Config fix'"
        }

        with patch('auto_fix_generator.FIXES_DIR', self.temp_fixes_dir):
            result = afg.save_fix_script(fix)
            script_file = Path(result)
            content = script_file.read_text(encoding='utf-8')
            self.assertIn("echo 'Config fix'", content)


class TestGenerateReport(unittest.TestCase):
    """测试报告生成功能"""

    def test_generate_report_with_fixes(self):
        """测试带修复的报告"""
        fixes = [
            {
                "category": "api_error",
                "name": "API 修复",
                "count": 2,
                "script": "#!/bin/bash\necho test"
            }
        ]
        result = afg.generate_report(fixes)
        self.assertIsInstance(result, str)
        self.assertIn("自动修复脚本生成报告", result)
        self.assertIn("生成的修复脚本", result)
        self.assertIn("API 修复", result)

    def test_generate_report_empty(self):
        """测试空修复报告"""
        result = afg.generate_report([])
        self.assertIsInstance(result, str)
        self.assertIn("自动修复脚本生成报告", result)
        self.assertIn("暂无", result)

    def test_generate_report_multiple_fixes(self):
        """测试多修复报告"""
        fixes = [
            {"category": "api_error", "name": "API 修复", "count": 2, "script": "test"},
            {"category": "config_error", "name": "配置修复", "count": 3, "script": "test"},
            {"category": "data_error", "name": "数据修复", "count": 2, "script": "test"},
        ]
        result = afg.generate_report(fixes)
        self.assertIn("API 修复", result)
        self.assertIn("配置修复", result)
        self.assertIn("数据修复", result)


class TestConstants(unittest.TestCase):
    """测试常量定义"""

    def test_workspace_defined(self):
        """测试工作空间路径定义"""
        self.assertIsInstance(afg.WORKSPACE, Path)

    def test_learnings_dir_defined(self):
        """测试学习目录定义"""
        self.assertIsInstance(afg.LEARNINGS_DIR, Path)

    def test_fixes_dir_defined(self):
        """测试修复目录定义"""
        self.assertIsInstance(afg.FIXES_DIR, Path)


class TestFixTemplatesContent(unittest.TestCase):
    """测试修复模板内容"""

    def test_api_template_contains_key_elements(self):
        """测试 API 模板包含关键元素"""
        template = afg.get_api_fix_template()
        self.assertIn("API", template)
        self.assertIn("echo", template)
        self.assertIn("修复", template)

    def test_config_template_contains_key_elements(self):
        """测试配置模板包含关键元素"""
        template = afg.get_config_fix_template()
        self.assertIn("配置", template)
        self.assertIn("echo", template)
        self.assertIn("修复", template)

    def test_data_template_contains_key_elements(self):
        """测试数据模板包含关键元素"""
        template = afg.get_data_fix_template()
        self.assertIn("数据", template)
        self.assertIn("echo", template)
        self.assertIn("修复", template)

    def test_file_template_contains_key_elements(self):
        """测试文件模板包含关键元素"""
        template = afg.get_file_fix_template()
        self.assertIn("文件", template)
        self.assertIn("echo", template)
        self.assertIn("修复", template)


class TestErrorCategories(unittest.TestCase):
    """测试错误分类"""

    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.temp_learnings_dir = Path(self.test_dir) / "learnings"
        self.temp_learnings_dir.mkdir()

    def tearDown(self):
        """清理临时目录"""
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('auto_fix_generator.LEARNINGS_DIR')
    def test_all_categories_detected(self, mock_dir):
        """测试所有分类都能检测"""
        mock_dir = self.temp_learnings_dir
        categories = [
            ("api", "api_error"),
            ("配置", "config_error"),
            ("数据", "data_error"),
            ("文件", "file_error"),
        ]

        for keyword, expected_cat in categories:
            test_file = self.temp_learnings_dir / f"{expected_cat}.md"
            test_file.write_text(f"Test with {keyword}", encoding='utf-8')

        with patch('auto_fix_generator.LEARNINGS_DIR', self.temp_learnings_dir):
            result = afg.analyze_for_fixes()
            self.assertIsInstance(result, list)


if __name__ == '__main__':
    unittest.main()
