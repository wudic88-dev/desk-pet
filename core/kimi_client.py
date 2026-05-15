"""Kimi API 客户端 - 封装对话和流式输出"""

import json
from dataclasses import dataclass
from typing import Generator, List, Optional

import httpx

from config import settings
from database.db_manager import DBManager
from utils.logger import setup_logger

logger = setup_logger()


@dataclass
class ChatMessage:
    """对话消息"""

    role: str  # "system", "user", "assistant"
    content: str


class KimiClient:
    """Kimi API 客户端

    兼容 OpenAI Chat Completions API 格式。
    支持普通请求和流式（SSE）输出。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self._api_key = api_key or settings.kimi_api_key
        self._base_url = (base_url or settings.kimi_base_url).rstrip("/")
        self._model = model or settings.kimi_model

        if not self._api_key:
            logger.warning("Kimi API Key 未配置，请在 .env 中设置 KIMI_API_KEY")

        self._client = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=10.0),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

        # 数据库
        self._db = DBManager()
        # 对话历史（从数据库加载）
        self._history: List[ChatMessage] = self._load_history_from_db()
        # 系统提示词
        self._system_prompt = (
            "你是一只可爱的桌面宠物猫咪，性格活泼、粘人、会撒娇。"
            "回答要简短（50字以内），多用emoji，语气像小猫说话。"
            "你可以陪主人聊天、解闷、提醒休息。"
        )

    # ---- 核心请求 ----

    def chat(
        self,
        user_message: str,
        stream: bool = True,
    ) -> Generator[str, None, None]:
        """发送对话请求

        Args:
            user_message: 用户输入的消息
            stream: 是否使用流式输出

        Yields:
            流式输出的文本片段（仅 stream=True 时有效）

        Raises:
            RuntimeError: API 调用失败
        """
        if not self._api_key:
            raise RuntimeError("API Key 未配置")

        messages = self._build_messages(user_message)
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": stream,
            "temperature": 0.8,
        }

        logger.info(f"发送请求: model={self._model}, stream={stream}")

        try:
            if stream:
                yield from self._chat_stream(payload)
            else:
                yield self._chat_sync(payload)
        except httpx.HTTPStatusError as e:
            logger.error(f"API 请求失败 [{e.response.status_code}]: {e.response.text}")
            raise RuntimeError(f"API 错误 [{e.response.status_code}]: {e.response.text}") from e
        except httpx.HTTPError as e:
            logger.error(f"网络请求失败: {e}")
            raise RuntimeError(f"网络请求失败: {e}") from e

    def _build_api_url(self) -> str:
        """构建 API URL，自动处理 base_url 是否已包含 /v1"""
        base = self._base_url
        if base.endswith("/v1"):
            base = base[:-3]
        return f"{base}/v1/chat/completions"

    def _chat_stream(self, payload: dict) -> Generator[str, None, None]:
        """流式请求，逐字返回"""
        url = self._build_api_url()
        with self._client.stream(
            "POST",
            url,
            json=payload,
        ) as response:
            if response.status_code >= 400:
                response.read()
                raise httpx.HTTPStatusError(
                    f"API error {response.status_code}",
                    request=response.request,
                    response=response,
                )

            full_content = ""
            for line in response.iter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        delta = (
                            chunk.get("choices", [{}])[0]
                            .get("delta", {})
                            .get("content", "")
                        )
                        if delta:
                            full_content += delta
                            yield delta
                    except json.JSONDecodeError:
                        continue

            # 保存到历史记录
            self._add_to_history("user", payload["messages"][-1]["content"])
            self._add_to_history("assistant", full_content)

    def _chat_sync(self, payload: dict) -> str:
        """普通请求，一次性返回"""
        url = self._build_api_url()
        response = self._client.post(
            url,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        self._add_to_history("user", payload["messages"][-1]["content"])
        self._add_to_history("assistant", content)
        return content

    # ---- 消息历史管理 ----

    def _build_messages(self, user_message: str) -> List[dict]:
        """构建请求消息列表"""
        messages = [{"role": "system", "content": self._system_prompt}]
        for msg in self._history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": user_message})
        return messages

    def _add_to_history(self, role: str, content: str):
        """添加消息到历史记录（同时持久化到数据库）"""
        msg = ChatMessage(role=role, content=content)
        self._history.append(msg)
        self._db.save_chat(role, content)
        # 限制历史长度，保留最近 20 轮
        max_history = 40
        if len(self._history) > max_history:
            self._history = self._history[-max_history:]

    def _load_history_from_db(self) -> List[ChatMessage]:
        """从数据库加载历史记录"""
        records = self._db.load_chat_history(limit=40)
        return [ChatMessage(role=r.role, content=r.content) for r in records]

    def clear_history(self):
        """清空对话历史（包括数据库）"""
        self._history.clear()
        self._db.clear_chat_history()
        logger.info("对话历史已清空")

    def get_history(self) -> List[ChatMessage]:
        """获取对话历史"""
        return list(self._history)

    # ---- 系统提示词 ----

    def set_system_prompt(self, prompt: str):
        """设置系统提示词"""
        self._system_prompt = prompt
        logger.info("系统提示词已更新")
