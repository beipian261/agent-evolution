@echo off
chcp 65001 >nul
echo 正在启动抖音AI自动回复助手...
python main.py
if errorlevel 1 (
    echo.
    echo 程序启动失败！请检查：
    echo 1. 是否安装了Python 3.8+
    echo 2. 是否安装了依赖包（pip install -r requirements.txt）
    echo.
    pause
)
