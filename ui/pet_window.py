from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout

from core.asset_manager import AssetManager
from database.db_manager import DBManager
from ui.animation_engine import AnimationEngine
from utils.logger import setup_logger

logger = setup_logger()


class PetWindow(QWidget):
    """宠物主窗口 - 透明、无边框、置顶、可拖拽"""

    pet_clicked = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_pos: QPoint = QPoint()
        self._drag_start_pos: QPoint = QPoint()
        self._has_dragged = False
        self._drag_threshold = 5
        self._db = DBManager()
        self.asset_manager = AssetManager()
        self.pet_size = self.asset_manager.get_display_size()
        self._setup_window()
        self._setup_ui()
        self._setup_animations()

    def _setup_window(self):
        """配置窗口属性：无边框、置顶、透明背景、固定小尺寸"""
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.pet_size, self.pet_size)
        # 恢复上次位置，否则默认屏幕右下角
        x = int(self._db.get_state("window_x", "0"))
        y = int(self._db.get_state("window_y", "0"))
        screen = self.screen().geometry()
        if x <= 0 or y <= 0:
            x = screen.width() - 120
            y = screen.height() - 120
        self.move(x, y)

    def _setup_ui(self):
        """设置 UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.pet_label = QLabel(self)
        self.pet_label.setFixedSize(self.pet_size, self.pet_size)
        self.pet_label.setAlignment(Qt.AlignCenter)
        self.pet_label.setStyleSheet("background-color: transparent; border: none;")
        layout.addWidget(self.pet_label)

        self.setCursor(Qt.PointingHandCursor)

    def _setup_animations(self):
        """初始化动画引擎并绑定帧变化事件"""
        self.anim_engine = AnimationEngine(self.asset_manager, self)
        self.anim_engine.set_label(self.pet_label)
        # 帧变化时同步更新窗口遮罩
        self.anim_engine.frame_changed.connect(self._update_mask)
        self.anim_engine.play("idle")
        logger.info("宠物窗口初始化完成")

    def _update_mask(self, _frame_idx=None):
        """根据当前图片的 alpha 通道更新窗口遮罩，只显示非透明区域"""
        pixmap = self.pet_label.pixmap()
        if not pixmap or pixmap.isNull():
            return
        # 使用 createHeuristicMask 从 alpha 通道精确生成遮罩
        mask = pixmap.createHeuristicMask()
        if not mask.isNull():
            self.setMask(mask)

    # ---- 鼠标事件 ----

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._drag_start_pos = event.globalPosition().toPoint()
            self._has_dragged = False
            self.anim_engine.play("click")
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            current_pos = event.globalPosition().toPoint()
            if not self._has_dragged:
                distance = (current_pos - self._drag_start_pos).manhattanLength()
                if distance > self._drag_threshold:
                    self._has_dragged = True
            self.move(current_pos - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self._has_dragged:
                # 拖拽结束，保存窗口位置
                pos = self.pos()
                self._db.set_state("window_x", str(pos.x()))
                self._db.set_state("window_y", str(pos.y()))
            elif self.pet_clicked:
                self.pet_clicked()
            event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        if self.anim_engine.current_state() is None:
            self.anim_engine.play("idle")
        # 窗口显示后更新遮罩
        QTimer.singleShot(50, self._update_mask)

    def hideEvent(self, event):
        super().hideEvent(event)
