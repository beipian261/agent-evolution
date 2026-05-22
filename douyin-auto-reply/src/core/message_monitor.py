import time
import json
import os
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Message:
    id: str
    type: str
    sender: str
    content: str
    timestamp: datetime
    replied: bool = False
    video_id: Optional[str] = None


class MessageMonitor:
    def __init__(self, config_manager, simulator_controller):
        self.config = config_manager
        self.simulator = simulator_controller
        self.messages: List[Message] = []
        self.processed_ids = set()
        self.running = False
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def load_processed_messages(self):
        history_path = self.config.get('database.history_path', 'data/history.json')
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_ids = set(item.get('id') for item in data)
            except Exception as e:
                logger.error(f"加载历史记录失败: {e}")

    def save_message(self, message: Message):
        history_path = self.config.get('database.history_path', 'data/history.json')
        history_data = []
        if os.path.exists(history_path):
            try:
                with open(history_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
            except Exception as e:
                logger.error(f"读取历史记录失败: {e}")

        history_data.append({
            'id': message.id,
            'type': message.type,
            'sender': message.sender,
            'content': message.content,
            'timestamp': message.timestamp.isoformat(),
            'replied': message.replied
        })

        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

    def scan_private_messages(self) -> List[Message]:
        new_messages = []
        if not self.config.get('monitor.enable_private_message', True):
            return new_messages

        logger.info("扫描私信...")

        try:
            if self.simulator.bring_to_front():
                time.sleep(1)

                test_messages = [
                    {
                        'id': f'pm_{int(time.time())}_{i}',
                        'sender': f'用户{i+1}',
                        'content': ['你好，这个多少钱？', '发货时间是多久？', '质量怎么样？'][i % 3],
                        'timestamp': datetime.now()
                    }
                    for i in range(2)
                ]

                for msg_data in test_messages:
                    if msg_data['id'] not in self.processed_ids:
                        msg = Message(
                            id=msg_data['id'],
                            type='private_message',
                            sender=msg_data['sender'],
                            content=msg_data['content'],
                            timestamp=msg_data['timestamp']
                        )
                        new_messages.append(msg)
                        self.messages.append(msg)
                        self.processed_ids.add(msg.id)
                        self.save_message(msg)

        except Exception as e:
            logger.error(f"扫描私信失败: {e}")

        return new_messages

    def scan_comments(self) -> List[Message]:
        new_messages = []
        if not self.config.get('monitor.enable_comment', True):
            return new_messages

        logger.info("扫描评论...")

        try:
            test_comments = [
                {
                    'id': f'comment_{int(time.time())}_{i}',
                    'sender': f'评论用户{i+1}',
                    'content': ['这个怎么买？', '尺码怎么选？', '好看！'][i % 3],
                    'timestamp': datetime.now(),
                    'video_id': f'video_{i+1}'
                }
                for i in range(2)
            ]

            for msg_data in test_comments:
                if msg_data['id'] not in self.processed_ids:
                    msg = Message(
                        id=msg_data['id'],
                        type='comment',
                        sender=msg_data['sender'],
                        content=msg_data['content'],
                        timestamp=msg_data['timestamp'],
                        video_id=msg_data['video_id']
                    )
                    new_messages.append(msg)
                    self.messages.append(msg)
                    self.processed_ids.add(msg.id)
                    self.save_message(msg)

        except Exception as e:
            logger.error(f"扫描评论失败: {e}")

        return new_messages

    def scan_all(self) -> List[Message]:
        all_new = []
        all_new.extend(self.scan_private_messages())
        all_new.extend(self.scan_comments())
        return all_new

    def start(self):
        self.running = True
        self.load_processed_messages()
        logger.info("消息监控已启动")

    def stop(self):
        self.running = False
        logger.info("消息监控已停止")

    def run_monitor_loop(self):
        check_interval = self.config.get('monitor.check_interval', 5)
        while self.running:
            try:
                new_messages = self.scan_all()
                if new_messages and self.callback:
                    self.callback(new_messages)
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
            time.sleep(check_interval)
