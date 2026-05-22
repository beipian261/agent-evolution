import sys
import threading
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QTableWidget,
    QTableWidgetItem, QLineEdit, QFormLayout, QGroupBox, QCheckBox,
    QSpinBox, QComboBox, QSplitter, QMessageBox, QFileDialog, QHeaderView
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QFont

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.config_manager import ConfigManager
from core.simulator_controller import SimulatorController
from core.message_monitor import MessageMonitor, Message
from core.reply_engine import ReplyEngine


class SignalHandler(QObject):
    new_message = pyqtSignal(object)
    log_message = pyqtSignal(str)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()
        self.simulator = SimulatorController(self.config)
        self.monitor = MessageMonitor(self.config, self.simulator)
        self.reply_engine = ReplyEngine(self.config)
        self.signals = SignalHandler()
        self.monitor_thread = None
        self.is_running = False

        self.init_ui()
        self.connect_signals()
        self.load_history()

    def init_ui(self):
        self.setWindowTitle(f"{self.config.get('app_name', '抖音AI自动回复助手')} v{self.config.get('version', '1.0.0')}")
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        control_layout = QHBoxLayout()
        self.status_label = QLabel("状态: 未启动")
        self.status_label.setStyleSheet("font-weight: bold; color: gray;")
        control_layout.addWidget(self.status_label)

        self.start_btn = QPushButton("启动监控")
        self.start_btn.clicked.connect(self.toggle_monitor)
        control_layout.addWidget(self.start_btn)

        self.find_window_btn = QPushButton("查找模拟器")
        self.find_window_btn.clicked.connect(self.find_simulator)
        control_layout.addWidget(self.find_window_btn)

        control_layout.addStretch()
        main_layout.addLayout(control_layout)

        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_messages_tab(), "消息记录")
        self.tab_widget.addTab(self.create_keywords_tab(), "关键词管理")
        self.tab_widget.addTab(self.create_settings_tab(), "系统设置")
        left_layout.addWidget(self.tab_widget)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        log_group = QGroupBox("运行日志")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 9))
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        right_layout.addWidget(log_group)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([800, 400])

        main_layout.addWidget(splitter)

    def create_messages_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.message_table = QTableWidget()
        self.message_table.setColumnCount(5)
        self.message_table.setHorizontalHeaderLabels(["时间", "类型", "发送者", "内容", "回复状态"])
        self.message_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.message_table.setAlternatingRowColors(True)
        layout.addWidget(self.message_table)

        return widget

    def create_keywords_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        form_layout = QFormLayout()
        self.keyword_input = QLineEdit()
        self.reply_input = QLineEdit()
        form_layout.addRow("关键词:", self.keyword_input)
        form_layout.addRow("回复内容:", self.reply_input)
        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加关键词")
        add_btn.clicked.connect(self.add_keyword)
        btn_layout.addWidget(add_btn)

        import_btn = QPushButton("批量导入")
        import_btn.clicked.connect(self.import_keywords)
        btn_layout.addWidget(import_btn)

        export_btn = QPushButton("导出关键词")
        export_btn.clicked.connect(self.export_keywords)
        btn_layout.addWidget(export_btn)
        layout.addLayout(btn_layout)

        self.keyword_table = QTableWidget()
        self.keyword_table.setColumnCount(3)
        self.keyword_table.setHorizontalHeaderLabels(["关键词", "回复内容", "操作"])
        self.keyword_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.refresh_keyword_table()
        layout.addWidget(self.keyword_table)

        return widget

    def create_settings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        simulator_group = QGroupBox("模拟器设置")
        simulator_layout = QFormLayout()
        self.window_title_input = QLineEdit(self.config.get('simulator.window_title', 'MuMuPlayer'))
        simulator_layout.addRow("窗口标题:", self.window_title_input)
        simulator_group.setLayout(simulator_layout)
        layout.addWidget(simulator_group)

        monitor_group = QGroupBox("监控设置")
        monitor_layout = QFormLayout()
        self.check_interval_spin = QSpinBox()
        self.check_interval_spin.setRange(1, 60)
        self.check_interval_spin.setValue(self.config.get('monitor.check_interval', 5))
        monitor_layout.addRow("检查间隔(秒):", self.check_interval_spin)

        self.enable_pm_check = QCheckBox("启用私信监控")
        self.enable_pm_check.setChecked(self.config.get('monitor.enable_private_message', True))
        monitor_layout.addRow("", self.enable_pm_check)

        self.enable_comment_check = QCheckBox("启用评论监控")
        self.enable_comment_check.setChecked(self.config.get('monitor.enable_comment', True))
        monitor_layout.addRow("", self.enable_comment_check)
        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)

        reply_group = QGroupBox("回复设置")
        reply_layout = QFormLayout()
        self.reply_mode_combo = QComboBox()
        self.reply_mode_combo.addItems(["ai", "keyword"])
        self.reply_mode_combo.setCurrentText(self.config.get('reply.mode', 'ai'))
        reply_layout.addRow("回复模式:", self.reply_mode_combo)

        self.min_delay_spin = QSpinBox()
        self.min_delay_spin.setRange(1, 60)
        self.min_delay_spin.setValue(self.config.get('reply.min_delay', 3))
        reply_layout.addRow("最小延迟(秒):", self.min_delay_spin)

        self.max_delay_spin = QSpinBox()
        self.max_delay_spin.setRange(1, 120)
        self.max_delay_spin.setValue(self.config.get('reply.max_delay', 12))
        reply_layout.addRow("最大延迟(秒):", self.max_delay_spin)

        self.ai_provider_combo = QComboBox()
        self.ai_provider_combo.addItems(["openai", "custom"])
        self.ai_provider_combo.setCurrentText(self.config.get('reply.ai_provider', 'openai'))
        reply_layout.addRow("AI提供商:", self.ai_provider_combo)

        self.api_key_input = QLineEdit(self.config.get('reply.ai_api_key', ''))
        self.api_key_input.setEchoMode(QLineEdit.Password)
        reply_layout.addRow("API密钥:", self.api_key_input)

        self.ai_model_input = QLineEdit(self.config.get('reply.ai_model', 'gpt-3.5-turbo'))
        reply_layout.addRow("AI模型:", self.ai_model_input)

        self.personality_input = QLineEdit(self.config.get('reply.ai_personality', '友好、亲切、自然'))
        reply_layout.addRow("回复风格:", self.personality_input)
        reply_group.setLayout(reply_layout)
        layout.addWidget(reply_group)

        safety_group = QGroupBox("安全设置")
        safety_layout = QFormLayout()
        self.enable_sensitive_check = QCheckBox("启用敏感词过滤")
        self.enable_sensitive_check.setChecked(self.config.get('safety.enable_sensitive_word_filter', True))
        safety_layout.addRow("", self.enable_sensitive_check)

        self.enable_random_delay_check = QCheckBox("启用随机延迟")
        self.enable_random_delay_check.setChecked(self.config.get('safety.enable_random_delay', True))
        safety_layout.addRow("", self.enable_random_delay_check)
        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)

        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        layout.addStretch()
        return widget

    def connect_signals(self):
        self.signals.new_message.connect(self.on_new_message)
        self.signals.log_message.connect(self.append_log)
        self.monitor.set_callback(self.handle_new_messages)

    def toggle_monitor(self):
        if self.is_running:
            self.stop_monitor()
        else:
            self.start_monitor()

    def start_monitor(self):
        self.log("正在启动监控...")
        self.monitor.start()
        self.is_running = True
        self.start_btn.setText("停止监控")
        self.status_label.setText("状态: 运行中")
        self.status_label.setStyleSheet("font-weight: bold; color: green;")

        self.monitor_thread = threading.Thread(target=self.monitor.run_monitor_loop, daemon=True)
        self.monitor_thread.start()
        self.log("监控已启动")

    def stop_monitor(self):
        self.log("正在停止监控...")
        self.monitor.stop()
        self.is_running = False
        self.start_btn.setText("启动监控")
        self.status_label.setText("状态: 已停止")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        self.log("监控已停止")

    def find_simulator(self):
        self.log("正在查找模拟器窗口...")
        handle = self.simulator.find_simulator_window()
        if handle:
            rect = self.simulator.get_window_rect()
            self.log(f"找到模拟器: {rect}")
            QMessageBox.information(self, "成功", f"找到模拟器窗口！\n位置: {rect}")
        else:
            self.log("未找到模拟器窗口")
            QMessageBox.warning(self, "提示", "未找到模拟器窗口，请确保模拟器已启动")

    def handle_new_messages(self, messages):
        for msg in messages:
            self.signals.new_message.emit(msg)
            self.process_reply(msg)

    def on_new_message(self, msg: Message):
        row = self.message_table.rowCount()
        self.message_table.insertRow(row)
        self.message_table.setItem(row, 0, QTableWidgetItem(msg.timestamp.strftime("%H:%M:%S")))
        self.message_table.setItem(row, 1, QTableWidgetItem("私信" if msg.type == "private_message" else "评论"))
        self.message_table.setItem(row, 2, QTableWidgetItem(msg.sender))
        self.message_table.setItem(row, 3, QTableWidgetItem(msg.content))
        self.message_table.setItem(row, 4, QTableWidgetItem("待回复"))

    def process_reply(self, msg: Message):
        self.log(f"收到新消息: {msg.sender} - {msg.content}")
        reply = self.reply_engine.generate_reply(msg.content)

        if reply:
            delay = self.reply_engine.get_random_delay()
            self.log(f"将在 {delay:.1f} 秒后回复: {reply}")

            def delayed_reply():
                import time
                time.sleep(delay)
                self.log(f"已回复: {reply}")
                for row in range(self.message_table.rowCount()):
                    if self.message_table.item(row, 3).text() == msg.content:
                        self.message_table.setItem(row, 4, QTableWidgetItem("已回复"))
                        break

            thread = threading.Thread(target=delayed_reply, daemon=True)
            thread.start()
        else:
            self.log("未生成回复")

    def add_keyword(self):
        keyword = self.keyword_input.text().strip()
        reply = self.reply_input.text().strip()
        if keyword and reply:
            self.reply_engine.add_keyword(keyword, reply)
            self.keyword_input.clear()
            self.reply_input.clear()
            self.refresh_keyword_table()
            self.log(f"添加关键词: {keyword}")

    def refresh_keyword_table(self):
        self.keyword_table.setRowCount(0)
        for item in self.reply_engine.keywords:
            row = self.keyword_table.rowCount()
            self.keyword_table.insertRow(row)
            self.keyword_table.setItem(row, 0, QTableWidgetItem(item['keyword']))
            self.keyword_table.setItem(row, 1, QTableWidgetItem(item['reply']))

            delete_btn = QPushButton("删除")
            delete_btn.clicked.connect(lambda _, kw=item['keyword']: self.delete_keyword(kw))
            self.keyword_table.setCellWidget(row, 2, delete_btn)

    def delete_keyword(self, keyword):
        self.reply_engine.remove_keyword(keyword)
        self.refresh_keyword_table()
        self.log(f"删除关键词: {keyword}")

    def import_keywords(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入关键词", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        if 'keyword' in item and 'reply' in item:
                            self.reply_engine.add_keyword(item['keyword'], item['reply'])
                    self.refresh_keyword_table()
                    self.log(f"导入关键词成功: {len(data)} 条")
            except Exception as e:
                self.log(f"导入失败: {e}")

    def export_keywords(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出关键词", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.reply_engine.keywords, f, ensure_ascii=False, indent=2)
                self.log("导出关键词成功")
            except Exception as e:
                self.log(f"导出失败: {e}")

    def save_settings(self):
        self.config.set('simulator.window_title', self.window_title_input.text())
        self.config.set('monitor.check_interval', self.check_interval_spin.value())
        self.config.set('monitor.enable_private_message', self.enable_pm_check.isChecked())
        self.config.set('monitor.enable_comment', self.enable_comment_check.isChecked())
        self.config.set('reply.mode', self.reply_mode_combo.currentText())
        self.config.set('reply.min_delay', self.min_delay_spin.value())
        self.config.set('reply.max_delay', self.max_delay_spin.value())
        self.config.set('reply.ai_provider', self.ai_provider_combo.currentText())
        self.config.set('reply.ai_api_key', self.api_key_input.text())
        self.config.set('reply.ai_model', self.ai_model_input.text())
        self.config.set('reply.ai_personality', self.personality_input.text())
        self.config.set('safety.enable_sensitive_word_filter', self.enable_sensitive_check.isChecked())
        self.config.set('safety.enable_random_delay', self.enable_random_delay_check.isChecked())
        self.config.save_config()
        self.log("设置已保存")
        QMessageBox.information(self, "成功", "设置已保存！")

    def load_history(self):
        history_path = self.config.get('database.history_path', 'data/history.json')
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data[-50:]:
                        from datetime import datetime
                        ts = datetime.fromisoformat(item['timestamp'])
                        row = self.message_table.rowCount()
                        self.message_table.insertRow(row)
                        self.message_table.setItem(row, 0, QTableWidgetItem(ts.strftime("%H:%M:%S")))
                        self.message_table.setItem(row, 1, QTableWidgetItem("私信" if item['type'] == "private_message" else "评论"))
                        self.message_table.setItem(row, 2, QTableWidgetItem(item['sender']))
                        self.message_table.setItem(row, 3, QTableWidgetItem(item['content']))
                        self.message_table.setItem(row, 4, QTableWidgetItem("已回复" if item.get('replied') else "待回复"))
            except Exception as e:
                self.log(f"加载历史记录失败: {e}")

    def log(self, message: str):
        self.signals.log_message.emit(message)

    def append_log(self, message: str):
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
