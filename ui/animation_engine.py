from typing import Optional

from PySide6.QtCore import QTimer, QObject, Signal
from PySide6.QtWidgets import QLabel

from core.asset_manager import AssetManager
from utils.logger import setup_logger

logger = setup_logger()


class AnimationEngine(QObject):
    """帧动画引擎 - 只负责播放逻辑，素材管理委托给 AssetManager"""

    frame_changed = Signal(int)
    state_changed = Signal(str)
    animation_finished = Signal(str)

    def __init__(self, asset_manager: AssetManager, parent=None):
        super().__init__(parent)
        self._asset_manager = asset_manager
        self._current_state: Optional[str] = None
        self._current_frame = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_timer)
        self._label: Optional[QLabel] = None

    def set_label(self, label: QLabel):
        self._label = label

    def play(self, state_name: str):
        states = self._asset_manager.get_states()
        if state_name not in states:
            logger.warning(f"未知动画状态: {state_name}")
            return
        if self._current_state == state_name:
            return

        self._timer.stop()
        self._current_state = state_name
        self._current_frame = 0
        self.state_changed.emit(state_name)

        config = self._asset_manager.get_state_config(state_name)
        if config:
            self._update_frame()
            self._timer.start(config.frame_duration_ms)
            logger.debug(f"切换到动画状态: {state_name}")

    def _on_timer(self):
        if not self._current_state:
            return

        config = self._asset_manager.get_state_config(self._current_state)
        frames = self._asset_manager.get_frames(self._current_state)

        if not frames:
            return

        self._current_frame += 1

        if self._current_frame >= len(frames):
            if config and config.loop:
                self._current_frame = 0
            else:
                self._current_frame = len(frames) - 1
                self._timer.stop()
                self.animation_finished.emit(self._current_state)
                if config and config.return_to:
                    self.play(config.return_to)
                return

        self._update_frame()
        self.frame_changed.emit(self._current_frame)

    def _update_frame(self):
        if not self._label or not self._current_state:
            return
        frames = self._asset_manager.get_frames(self._current_state)
        if self._current_frame < len(frames):
            self._label.setPixmap(frames[self._current_frame])

    def current_state(self) -> Optional[str]:
        return self._current_state

    def get_states(self):
        return self._asset_manager.get_states()
