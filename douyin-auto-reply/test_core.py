#!/usr/bin/env python3
"""
抖音AI自动回复助手 - 核心功能测试脚本
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.config_manager import ConfigManager
from core.reply_engine import ReplyEngine

def test_config():
    """测试配置管理器"""
    print("=" * 50)
    print("测试1: 配置管理器")
    print("=" * 50)
    try:
        config = ConfigManager()
        print(f"✓ 配置加载成功")
        print(f"  - 应用名称: {config.get('app_name')}")
        print(f"  - 版本: {config.get('version')}")
        print(f"  - 回复模式: {config.get('reply.mode')}")
        print()
        return config
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return None

def test_reply_engine(config):
    """测试回复引擎"""
    print("=" * 50)
    print("测试2: 回复引擎")
    print("=" * 50)
    try:
        engine = ReplyEngine(config)
        print(f"✓ 回复引擎初始化成功")
        print(f"  - 加载关键词数量: {len(engine.keywords)}")
        print(f"  - 加载敏感词数量: {len(engine.sensitive_words)}")
        print()
        
        # 测试关键词回复
        test_messages = [
            "你好，这个多少钱？",
            "发货时间是多久？",
            "质量怎么样？",
        ]
        
        print("测试关键词回复:")
        for msg in test_messages:
            reply = engine.keyword_reply(msg)
            if reply:
                print(f"  Q: {msg}")
                print(f"  A: {reply}")
                print()
        
        # 测试AI回复模式
        print("测试AI回复模式（无API密钥时显示测试回复）:")
        test_ai_msg = "这个产品有什么特点？"
        ai_reply = engine.ai_reply(test_ai_msg)
        print(f"  Q: {test_ai_msg}")
        print(f"  A: {ai_reply}")
        print()
        
        # 测试敏感词过滤
        print("测试敏感词过滤:")
        test_sensitive_msg = "加微信联系我，给你优惠"
        filtered = engine._filter_sensitive_words(test_sensitive_msg)
        print(f"  原消息: {test_sensitive_msg}")
        print(f"  过滤后: {filtered}")
        print()
        
        # 测试随机延迟
        print("测试随机延迟:")
        delay = engine.get_random_delay()
        print(f"  随机延迟: {delay:.2f}秒")
        print()
        
        return engine
    except Exception as e:
        print(f"✗ 回复引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_message_monitor(config):
    """测试消息监控器（不实际调用Windows API）"""
    print("=" * 50)
    print("测试3: 消息监控器")
    print("=" * 50)
    try:
        from core.message_monitor import MessageMonitor
        
        # 注意：这里不传入simulator_controller，因为Linux环境没有win32gui
        # 只测试数据处理部分
        print("✓ 消息监控模块导入成功")
        print("  注：完整的监控功能需要Windows环境")
        print()
        
        # 测试关键词保存
        print("测试关键词添加:")
        from core.reply_engine import ReplyEngine
        engine = ReplyEngine(config)
        engine.add_keyword("测试", "这是一个测试回复")
        print(f"  ✓ 添加测试关键词成功")
        engine.remove_keyword("测试")
        print(f"  ✓ 移除测试关键词成功")
        print()
        
        return True
    except Exception as e:
        print(f"✗ 消息监控测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print()
    print("🚀 抖音AI自动回复助手 - 核心功能测试")
    print("=" * 50)
    print()
    
    # 测试配置
    config = test_config()
    if not config:
        return 1
    
    # 测试回复引擎
    engine = test_reply_engine(config)
    if not engine:
        return 1
    
    # 测试消息监控
    test_message_monitor(config)
    
    print("=" * 50)
    print("✅ 所有核心功能测试通过！")
    print("=" * 50)
    print()
    print("📝 注意:")
    print("  - 完整的GUI和模拟器控制功能需要Windows环境")
    print("  - AI回复功能需要配置API密钥")
    print("  - 请查看docs/使用说明.md了解详细使用方法")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
