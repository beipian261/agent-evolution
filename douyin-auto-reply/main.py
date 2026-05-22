#!/usr/bin/env python3
"""
抖音AI自动回复助手 - 主程序入口
"""
import sys
import os

def check_environment():
    """检查运行环境"""
    import platform
    
    print("=" * 60)
    print("抖音AI自动回复助手 v1.0.0")
    print("=" * 60)
    print()
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print()
    
    # 检查是否有图形显示
    has_display = True
    if platform.system() == 'Linux':
        if 'DISPLAY' not in os.environ:
            has_display = False
    
    return has_display, platform.system()

def main():
    """主函数"""
    has_display, system = check_environment()
    
    if not has_display:
        print("⚠️  警告: 未检测到图形显示环境")
        print()
        print("📋 这是一个PyQt5桌面GUI应用程序，需要图形界面才能运行。")
        print()
        print("💡 解决方案:")
        print("  1. 将项目复制到Windows电脑运行")
        print("  2. 或者在有图形显示的Linux/macOS环境运行")
        print("  3. 或者使用远程桌面连接到有图形界面的系统")
        print()
        print("🧪 想测试核心功能？运行: python test_core.py")
        print()
        print("=" * 60)
        
        # 询问用户是否运行测试
        try:
            choice = input("是否运行核心功能测试？(y/n): ").strip().lower()
            if choice == 'y':
                print()
                os.system(f"{sys.executable} test_core.py")
        except KeyboardInterrupt:
            print("\n\n程序已退出")
        return 1
    
    # 有图形显示，启动GUI
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        print("❌ 错误: PyQt5未安装")
        print("请运行: pip install PyQt5")
        return 1
    
    # 添加src目录到路径
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    from gui.main_window import main as gui_main
    return gui_main()

if __name__ == "__main__":
    sys.exit(main())
