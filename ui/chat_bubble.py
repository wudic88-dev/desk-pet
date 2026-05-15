"""气泡对话框 - 宠物上方的聊天窗口"""

import markdown
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from core.chat_worker import ChatWorker
from core.ai_client import AIClient
from utils.logger import setup_logger

logger = setup_logger()


class ChatBubble(QWidget):
    """气泡对话框

    外观：圆角气泡 + 底部小三角，出现在宠物上方。
    功能：显示对话、输入消息、流式输出 AI 回复。
    """

    # 信号：气泡关闭时通知外部
    closed = Signal()

    def __init__(self, pet_window: QWidget, parent=None):
        super().__init__(parent)
        self._pet = pet_window
        self._client = AIClient()
        self._worker: ChatWorker | None = None
        self._current_reply = ""

        self._setup_window()
        self._setup_ui()
        self._setup_style()
        self._position_near_pet()

    # ---- 窗口配置 ----

    def _setup_window(self):
        """配置窗口属性"""
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(320, 420)

    def _setup_ui(self):
        """构建内部 UI"""
        # 主布局（留出边距给气泡边框）
        margin = 16
        layout = QVBoxLayout(self)
        layout.setContentsMargins(margin, margin, margin, margin + 12)
        layout.setSpacing(8)

        # 对话显示区域
        self.chat_display = QTextBrowser(self)
        self.chat_display.setReadOnly(True)
        self.chat_display.setOpenExternalLinks(True)
        layout.addWidget(self.chat_display, 1)

        # 输入区域
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)

        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("和小橘说点什么...")
        self.input_field.returnPressed.connect(self._on_send)
        input_layout.addWidget(self.input_field, 1)

        self.send_btn = QPushButton("发送", self)
        self.send_btn.setFixedWidth(60)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self._on_send)
        input_layout.addWidget(self.send_btn)

        layout.addLayout(input_layout)

        # 初始欢迎语
        self._append_message("assistant", "喵~ 主人好！我是小橘，有什么想和我说的吗？")

    def _setup_style(self):
        """应用样式"""
        self.chat_display.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                border: none;
                font-size: 14px;
                line-height: 1.6;
            }
        """)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 6px 10px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #ffab91;
            }
        """)
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff8a65;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff7043;
            }
            QPushButton:pressed {
                background-color: #f4511e;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)

    # ---- 气泡绘制 ----

    def paintEvent(self, event):
        """绘制圆角气泡 + 底部小三角"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        radius = 16
        tail_width = 20
        tail_height = 12

        # 气泡主体路径
        path = QPainterPath()
        path.moveTo(radius, 0)
        path.lineTo(rect.width() - radius, 0)
        path.arcTo(rect.width() - 2 * radius, 0, 2 * radius, 2 * radius, 90, -90)
        path.lineTo(rect.width(), rect.height() - radius - tail_height)
        path.arcTo(
            rect.width() - 2 * radius,
            rect.height() - 2 * radius - tail_height,
            2 * radius,
            2 * radius,
            0,
            -90,
        )

        # 底部小三角（居中）
        tail_center = rect.width() / 2
        path.lineTo(tail_center + tail_width / 2, rect.height() - tail_height)
        path.lineTo(tail_center, rect.height())
        path.lineTo(tail_center - tail_width / 2, rect.height() - tail_height)

        path.lineTo(radius, rect.height() - tail_height)
        path.arcTo(0, rect.height() - 2 * radius - tail_height, 2 * radius, 2 * radius, -90, -90)
        path.lineTo(0, radius)
        path.arcTo(0, 0, 2 * radius, 2 * radius, 180, -90)
        path.closeSubpath()

        # 填充背景
        painter.fillPath(path, QColor(255, 255, 255, 250))

        # 画边框
        pen = QPen(QColor(230, 230, 230))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)

    # ---- 位置管理 ----

    def _position_near_pet(self):
        """将气泡定位在宠物上方"""
        pet_geo = self._pet.geometry()
        bubble_x = pet_geo.center().x() - self.width() // 2
        bubble_y = pet_geo.top() - self.height() - 4

        # 边界检查：确保不超出屏幕左/右边界
        screen = self.screen().geometry()
        bubble_x = max(8, min(bubble_x, screen.width() - self.width() - 8))

        # 如果上方空间不够，显示在宠物下方
        if bubble_y < 8:
            bubble_y = pet_geo.bottom() + 4

        self.move(bubble_x, bubble_y)

    def showEvent(self, event):
        super().showEvent(event)
        self._position_near_pet()
        self.input_field.setFocus()

    # ---- 消息处理 ----

    def _append_message(self, role: str, content: str):
        """追加消息到显示区域"""
        prefix = "🐱 **小橘**" if role == "assistant" else "👤 **我**"
        color = "#e65100" if role == "assistant" else "#1565c0"

        # Markdown 转 HTML
        html_content = markdown.markdown(content, extensions=["nl2br"])

        block = f"""
        <div style="margin: 8px 0;">
            <span style="color: {color}; font-weight: bold;">{prefix}</span>
            <div style="margin-top: 4px; color: #333;">{html_content}</div>
        </div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 8px 0;">
        """

        self.chat_display.append(block)
        # 滚动到底部
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _append_chunk(self, chunk: str):
        """追加流式输出片段"""
        self._current_reply += chunk
        # 重新渲染当前回复（找到最后一条 assistant 消息并更新）
        self._refresh_last_reply()

    def _refresh_last_reply(self):
        """刷新最后一条回复的显示"""
        # 简单方案：清空并重新渲染所有历史
        self.chat_display.clear()
        for msg in self._client.get_history():
            self._append_message(msg.role, msg.content)
        # 加上当前正在生成的回复
        if self._current_reply:
            self._append_message("assistant", self._current_reply + "▌")

    def _on_send(self):
        """发送按钮点击 / 回车"""
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()
        self._append_message("user", text)

        # 禁用输入
        self.input_field.setEnabled(False)
        self.send_btn.setEnabled(False)
        self._current_reply = ""

        # 启动后台线程
        self._worker = ChatWorker(self._client, text, parent=self)
        self._worker.response_chunk.connect(self._append_chunk)
        self._worker.response_done.connect(self._on_response_done)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

        logger.info(f"用户发送: {text[:50]}")

    def _on_response_done(self):
        """流式输出完成"""
        self._current_reply = ""
        self._restore_input()
        self._refresh_last_reply()
        logger.info("AI 回复完成")

    def _on_error(self, error_msg: str):
        """处理错误"""
        self._current_reply = ""
        self._restore_input()
        self._append_message("assistant", f"呜... 出错了: {error_msg}")
        logger.error(f"聊天错误: {error_msg}")

    def _restore_input(self):
        """恢复输入状态"""
        self.input_field.setEnabled(True)
        self.send_btn.setEnabled(True)
        self.input_field.setFocus()
        if self._worker:
            self._worker.deleteLater()
            self._worker = None

    # ---- 公共接口 ----

    def closeEvent(self, event):
        """关闭时停止工作线程"""
        if self._worker and self._worker.isRunning():
            self._worker.stop()
        self.closed.emit()
        super().closeEvent(event)
