"""聊天工作线程 - 在后台线程中调用 Kimi API，避免阻塞 GUI"""

from PySide6.QtCore import QThread, Signal

from core.kimi_client import KimiClient
from utils.logger import setup_logger

logger = setup_logger()


class ChatWorker(QThread):
    """后台聊天工作线程

    流式输出通过信号逐字传回主线程：
    - response_chunk: 每个文本片段
    - response_done: 流式输出结束
    - error_occurred: 发生错误
    """

    response_chunk = Signal(str)
    response_done = Signal()
    error_occurred = Signal(str)

    def __init__(self, client: KimiClient, user_message: str, parent=None):
        super().__init__(parent)
        self._client = client
        self._user_message = user_message
        self._is_running = False

    def run(self):
        """在后台线程中执行 API 调用"""
        self._is_running = True
        logger.info(f"ChatWorker 开始处理: {self._user_message[:30]}...")

        try:
            for chunk in self._client.chat(self._user_message, stream=True):
                if not self._is_running:
                    logger.info("ChatWorker 被中断")
                    break
                self.response_chunk.emit(chunk)
            self.response_done.emit()
        except RuntimeError as e:
            logger.error(f"ChatWorker 错误: {e}")
            self.error_occurred.emit(str(e))
        except Exception as e:
            logger.error(f"ChatWorker 未知错误: {e}")
            self.error_occurred.emit(f"未知错误: {e}")

    def stop(self):
        """请求中断"""
        self._is_running = False
        self.wait(1000)
