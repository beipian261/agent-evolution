# 🖥️ Windows本地安装运行指南

## 🎯 您的电脑配置检查
✅ Windows 64位系统  
✅ 8GB 内存  
✅ Intel i5 处理器  
✅ 完全满足运行要求！

---

## 📦 第一步：获取项目文件

### 方法1：下载整个文件夹
将 `/workspace/douyin-auto-reply/` 整个文件夹复制到您的电脑，比如：
`D:\douyin-auto-reply\`

### 方法2：逐个复制文件
如果无法直接下载，请确保复制以下文件结构：

```
douyin-auto-reply/
├── main.py                    ← 主程序
├── requirements.txt           ← 依赖列表
├── build.spec                ← 打包配置
├── 启动.bat                   ← Windows启动脚本
├── test_core.py              ← 测试程序
├── config/
│   └── config.json           ← 配置文件
├── data/
│   ├── keywords.json         ← 关键词
│   └── sensitive_words.txt    ← 敏感词
└── src/
    ├── core/
    │   ├── simulator_controller.py
    │   ├── message_monitor.py
    │   └── reply_engine.py
    ├── gui/
    │   └── main_window.py
    ├── utils/
    │   └── config_manager.py
    └── __init__.py
```

---

## 🔧 第二步：安装Python

1. **下载Python**
   - 访问：https://www.python.org/downloads/
   - 下载Python 3.8或更高版本（推荐3.10或3.11）
   - 选择 "Windows installer (64-bit)"

2. **安装Python（重要！）**
   - ✅ **勾选 "Add Python to PATH"**
   - 点击 "Install Now"
   - 等待安装完成

3. **验证安装**
   - 按 `Win + R` 键
   - 输入 `cmd` 回车
   - 输入 `python --version`
   - 应该显示类似 `Python 3.10.x`

---

## 📦 第三步：安装依赖

1. **打开命令提示符**
   - 按 `Win + R`
   - 输入 `cmd` 回车

2. **进入项目文件夹**
   ```bash
   d:                           ← 假设您放在D盘
   cd douyin-auto-reply         ← 进入项目文件夹
   ```

3. **安装依赖包**
   ```bash
   pip install -r requirements.txt
   ```

   这个过程可能需要几分钟，请耐心等待。

---

## 🚀 第四步：运行程序

### 方法1：使用启动脚本（推荐）
直接双击项目文件夹中的 `启动.bat` 文件！

### 方法2：命令行运行
在项目文件夹中打开命令提示符，运行：
```bash
python main.py
```

### 方法3：先测试核心功能
如果想先测试，运行：
```bash
python test_core.py
```

---

## 🎨 第五步：使用程序

程序启动后，您会看到：

1. **主窗口界面**
   - 左侧：三个标签页（消息记录、关键词管理、系统设置）
   - 右侧：运行日志

2. **配置设置**
   - 点击"系统设置"标签
   - 根据需要配置参数
   - 点击"保存设置"

3. **启动监控**
   - 确保您的安卓模拟器已启动（如MuMu）
   - 点击"查找模拟器"按钮
   - 点击"启动监控"按钮

---

## 📦 可选：打包成EXE

如果您想打包成独立的EXE文件，方便分发：

1. **安装打包工具**
   ```bash
   pip install pyinstaller
   ```

2. **打包程序**
   ```bash
   pyinstaller build.spec
   ```

3. **获取EXE**
   - 在 `dist` 文件夹中找到 `抖音AI自动回复助手.exe`
   - 可以将这个EXE复制到任何Windows电脑运行，无需安装Python

---

## ❓ 常见问题

### Q: 提示找不到python命令？
A: 安装Python时没有勾选 "Add Python to PATH"，请重新安装并确保勾选。

### Q: pip安装很慢？
A: 使用国内镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 提示缺少某个模块？
A: 单独安装缺失的模块，例如：
```bash
pip install PyQt5
pip install pyautogui
pip install openai
```

### Q: 找不到模拟器窗口？
A:
1. 确保模拟器已启动
2. 在"系统设置"中检查窗口标题是否正确
3. 点击"查找模拟器"按钮

### Q: AI回复功能不工作？
A: 需要在"系统设置"中配置您的OpenAI API密钥。

---

## 🎉 完成！

现在您应该可以看到完整的GUI界面了！

如有问题，请查看项目中的其他文档：
- `README.md` - 项目介绍
- `docs/使用说明.md` - 详细使用说明
- `GUI_PREVIEW.md` - 界面预览

祝您使用愉快！
