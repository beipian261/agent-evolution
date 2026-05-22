# 抖音AI自动回复助手

一款基于Python开发的抖音智能回复工具，支持模拟器自动化操作、关键词回复、AI智能回复等功能。

## 项目结构

```
douyin-auto-reply/
├── config/              # 配置文件目录
│   └── config.json      # 主配置文件
├── data/                # 数据目录
│   ├── keywords.json    # 关键词数据
│   ├── sensitive_words.txt  # 敏感词库
│   └── history.json     # 历史记录（运行时生成）
├── src/                 # 源代码
│   ├── core/            # 核心模块
│   │   ├── simulator_controller.py  # 模拟器控制
│   │   ├── message_monitor.py       # 消息监控
│   │   └── reply_engine.py          # 回复引擎
│   ├── gui/             # 图形界面
│   │   └── main_window.py           # 主窗口
│   └── utils/           # 工具模块
│       └── config_manager.py        # 配置管理
├── docs/                # 文档目录
│   └── 使用说明.md      # 使用说明
├── main.py              # 程序入口
├── requirements.txt     # 依赖包列表
└── build.spec           # PyInstaller打包配置
```

## 功能特性

### 1. 账号登录
- 支持模拟器内正常登录抖音账号
- 扫码/密码登录均可使用
- 日常登录无阻碍

### 2. 自动监控抓取
- 实时监控粉丝私信消息
- 实时监控作品评论
- 自动保存消息历史

### 3. 双模式智能回复
- **固定关键词回复**：自定义关键词和回复内容，精准秒答
- **AI智能自由回复**：接入OpenAI等大模型，自然语境回复

### 4. 安全设置
- 自定义随机回复间隔（3-12秒）
- 自动过滤敏感词
- 可自由启停回复功能

### 5. 基础管理功能
- 话术批量导入/导出
- 回复历史记录查看
- 后台静默挂机运行

## 快速开始

### 环境要求
- Windows 10/11
- Python 3.8+
- 安卓模拟器（推荐MuMu模拟器）

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python main.py
```

### 打包成EXE
```bash
pip install pyinstaller
pyinstaller build.spec
```

## 详细说明

请查看 [docs/使用说明.md](docs/使用说明.md) 了解详细使用方法。

## 技术栈

- **GUI框架**：PyQt5
- **自动化操作**：pyautogui, win32gui
- **AI集成**：OpenAI API
- **其他**：requests, schedule, Pillow

## 免责声明

本软件仅供学习和研究使用，使用本软件产生的一切后果由使用者自行承担。请遵守抖音平台规则，合理使用。

## 许可证

本项目仅供学习交流使用。
