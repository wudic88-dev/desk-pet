import os

from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon, QAction

from utils.logger import setup_logger

logger = setup_logger()


class TrayManager:
    """系统托盘管理器"""

    def __init__(self, app: QApplication, parent=None):
        self.app = app
        self.parent = parent
        self.tray = QSystemTrayIcon(parent)
        self._setup_icon()
        self._setup_menu()
        self.tray.activated.connect(self._on_activated)

    def _setup_icon(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, "assets", "icons", "tray_icon.png")
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
            logger.info(f"托盘图标已加载: {icon_path}")
        else:
            logger.warning(f"托盘图标不存在: {icon_path}")
        self.tray.setToolTip("桌宠小橘")

    def _setup_menu(self):
        self.menu = QMenu()
        self.toggle_action = QAction("显示/隐藏", self.menu)
        self.toggle_action.triggered.connect(self._on_toggle)
        self.menu.addAction(self.toggle_action)
        self.menu.addSeparator()
        self.settings_action = QAction("设置", self.menu)
        self.settings_action.triggered.connect(self._on_settings)
        self.menu.addAction(self.settings_action)
        self.history_action = QAction("对话历史", self.menu)
        self.history_action.triggered.connect(self._on_history)
        self.menu.addAction(self.history_action)
        self.menu.addSeparator()
        self.quit_action = QAction("退出", self.menu)
        self.quit_action.triggered.connect(self._on_quit)
        self.menu.addAction(self.quit_action)
        self.tray.setContextMenu(self.menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason):
        if reason == QSystemTrayIcon.DoubleClick:
            self._on_toggle()

    def _on_toggle(self):
        if self.parent:
            if self.parent.isVisible():
                self.parent.hide()
            else:
                self.parent.show()
                self.parent.raise_()
                self.parent.activateWindow()

    def _on_settings(self):
        logger.info("打开设置面板")
        if self.parent and hasattr(self.parent, "show_settings"):
            self.parent.show_settings()

    def _on_history(self):
        logger.info("打开对话历史")
        if self.parent and hasattr(self.parent, "show_history"):
            self.parent.show_history()

    def _on_quit(self):
        logger.info("退出应用")
        self.tray.hide()
        self.app.quit()

    def show(self):
        self.tray.show()
        logger.info("系统托盘已显示")

    def show_message(self, title: str, message: str, duration: int = 3000):
        self.tray.showMessage(title, message, QSystemTrayIcon.Information, duration)
