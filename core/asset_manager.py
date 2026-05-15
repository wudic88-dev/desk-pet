import json
import os
from typing import Dict, List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from utils.logger import setup_logger

logger = setup_logger()


class PetStateConfig:
    """宠物动画状态配置"""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.folder = config.get("folder", name)
        self.prefix = config.get("prefix", name)
        self.frame_count = config.get("frames", 1)
        self.frame_duration_ms = config.get("frame_duration_ms", 500)
        self.loop = config.get("loop", True)
        self.return_to = config.get("return_to", None)


class AssetManager:
    """
    素材管理器 - 负责加载和管理宠物素材

    素材更换方式：
    1. 直接替换 assets/pet/ 下的 PNG 图片（同格式）
    2. 修改 assets/pet/pet_config.json 调整帧数、速度等
    3. 如需支持新格式（GIF/Live2D），继承此类并重写加载方法
    """

    def __init__(self, assets_dir: Optional[str] = None):
        self._assets_dir = assets_dir or self._default_assets_dir()
        self._pet_dir = os.path.join(self._assets_dir, "pet")
        self._config_path = os.path.join(self._pet_dir, "pet_config.json")

        self._pet_name: str = ""
        self._pet_source_size: int = 256
        self._display_size: int = 64
        self._states: Dict[str, PetStateConfig] = {}
        self._frames: Dict[str, List[QPixmap]] = {}

        self._load()

    @staticmethod
    def _default_assets_dir() -> str:
        """获取默认素材目录"""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_dir, "assets")

    def _load(self):
        """加载素材配置和帧图片"""
        self._states.clear()
        self._frames.clear()

        if not os.path.exists(self._config_path):
            logger.warning(f"素材配置不存在: {self._config_path}")
            return

        with open(self._config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self._pet_name = config.get("name", "小橘")
        self._pet_source_size = config.get("size", 256)

        for name, state_config in config.get("states", {}).items():
            self._states[name] = PetStateConfig(name, state_config)
            self._load_state_frames(name, state_config)

        logger.info(f"素材加载完成: {self._pet_name}, {len(self._states)} 个状态")

    def _load_state_frames(self, name: str, config: dict):
        """加载某一状态的帧图片"""
        folder = config.get("folder", name)
        prefix = config.get("prefix", name)
        frame_count = config.get("frames", 1)

        frames = []
        frame_dir = os.path.join(self._pet_dir, folder)

        for i in range(frame_count):
            path = os.path.join(frame_dir, f"{prefix}_{i}.png")
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # 缩放到目标显示尺寸
                    if self._display_size != self._pet_source_size:
                        pixmap = pixmap.scaled(
                            self._display_size,
                            self._display_size,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation,
                        )
                    frames.append(pixmap)
                else:
                    logger.warning(f"图片加载失败: {path}")
            else:
                logger.warning(f"帧图片不存在: {path}")

        self._frames[name] = frames
        logger.debug(f"状态 '{name}' 加载了 {len(frames)} 帧")

    # ---- 公共接口 ----

    def get_frames(self, state_name: str) -> List[QPixmap]:
        """获取某状态的帧列表"""
        return self._frames.get(state_name, [])

    def get_state_config(self, state_name: str) -> Optional[PetStateConfig]:
        """获取某状态的配置"""
        return self._states.get(state_name)

    def get_states(self) -> List[str]:
        """获取所有状态名"""
        return list(self._states.keys())

    def get_pet_name(self) -> str:
        """获取宠物名称"""
        return self._pet_name

    def get_source_size(self) -> int:
        """获取素材原始尺寸"""
        return self._pet_source_size

    def get_display_size(self) -> int:
        """获取当前显示尺寸"""
        return self._display_size

    def set_display_size(self, size: int):
        """设置显示尺寸（会重新加载素材）"""
        if size == self._display_size:
            return
        self._display_size = size
        self._load()
        logger.info(f"显示尺寸已调整为: {size}")

    def reload(self):
        """重新加载素材（更换素材文件后调用）"""
        self._load()
        logger.info("素材已重新加载")
