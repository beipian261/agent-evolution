import json
import os
import random
import logging
from typing import Optional, Dict, List
from openai import OpenAI
import requests

logger = logging.getLogger(__name__)


class ReplyEngine:
    def __init__(self, config_manager):
        self.config = config_manager
        self.keywords = self._load_keywords()
        self.sensitive_words = self._load_sensitive_words()

    def _load_keywords(self) -> List[Dict[str, str]]:
        keywords_path = self.config.get('database.keywords_path', 'data/keywords.json')
        if os.path.exists(keywords_path):
            try:
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载关键词失败: {e}")
        return []

    def _load_sensitive_words(self) -> List[str]:
        sensitive_path = 'data/sensitive_words.txt'
        if os.path.exists(sensitive_path):
            try:
                with open(sensitive_path, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
            except Exception as e:
                logger.error(f"加载敏感词失败: {e}")
        return []

    def save_keywords(self):
        keywords_path = self.config.get('database.keywords_path', 'data/keywords.json')
        try:
            with open(keywords_path, 'w', encoding='utf-8') as f:
                json.dump(self.keywords, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存关键词失败: {e}")

    def keyword_reply(self, message: str) -> Optional[str]:
        for item in self.keywords:
            if item['keyword'] in message:
                logger.info(f"关键词匹配: {item['keyword']}")
                return item['reply']
        return None

    def ai_reply(self, message: str) -> Optional[str]:
        provider = self.config.get('reply.ai_provider', 'openai')
        api_key = self.config.get('reply.ai_api_key', '')

        if not api_key:
            logger.warning("未设置AI API密钥")
            return None

        personality = self.config.get('reply.ai_personality', '友好、亲切、自然')
        model = self.config.get('reply.ai_model', 'gpt-3.5-turbo')
        temperature = self.config.get('reply.ai_temperature', 0.7)

        try:
            if provider == 'openai':
                return self._openai_reply(message, api_key, model, temperature, personality)
            else:
                return self._generic_ai_reply(message, api_key, personality)
        except Exception as e:
            logger.error(f"AI回复失败: {e}")
            return None

    def _openai_reply(self, message: str, api_key: str, model: str, temperature: float, personality: str) -> str:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"你是一个抖音客服助手，回复风格要{personality}。回答要简洁、友好，不要太长。"
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=temperature,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()

    def _generic_ai_reply(self, message: str, api_key: str, personality: str) -> str:
        test_replies = [
            "好的亲，我来帮您解答~",
            "这个问题我来跟您说一下哦",
            "好哒，稍等我帮您看看~",
            "感谢您的提问，让我来回答您~",
            "嗯嗯，这个我知道呢！"
        ]
        return random.choice(test_replies)

    def generate_reply(self, message: str) -> Optional[str]:
        mode = self.config.get('reply.mode', 'ai')

        if mode == 'keyword':
            reply = self.keyword_reply(message)
            if reply:
                return self._filter_sensitive_words(reply)
        elif mode == 'ai':
            reply = self.keyword_reply(message)
            if reply:
                return self._filter_sensitive_words(reply)
            reply = self.ai_reply(message)
            if reply:
                return self._filter_sensitive_words(reply)

        return None

    def _filter_sensitive_words(self, text: str) -> str:
        if not self.config.get('safety.enable_sensitive_word_filter', True):
            return text

        filtered = text
        for word in self.sensitive_words:
            filtered = filtered.replace(word, '*' * len(word))
        return filtered

    def add_keyword(self, keyword: str, reply: str):
        self.keywords.append({'keyword': keyword, 'reply': reply})
        self.save_keywords()

    def remove_keyword(self, keyword: str):
        self.keywords = [item for item in self.keywords if item['keyword'] != keyword]
        self.save_keywords()

    def get_random_delay(self) -> float:
        min_delay = self.config.get('reply.min_delay', 3)
        max_delay = self.config.get('reply.max_delay', 12)
        return random.uniform(min_delay, max_delay)
