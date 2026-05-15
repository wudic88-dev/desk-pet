"""设置面板 - 修改 API Key、宠物性格、尺寸等配置"""

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QGroupBox,
    QVBoxLayout,
)

from database.db_manager import DBManager
from utils.logger import setup_logger

logger = setup_logger()


class SettingsDialog(QDialog):
    """设置面板对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._db = DBManager()
        self.setWindowTitle("小橘设置")
        self.setFixedSize(480, 520)
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # ---- AI 配置 ----
        ai_group = QGroupBox("AI 配置")
        ai_layout = QFormLayout(ai_group)
        ai_layout.setSpacing(8)

        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("sk-...")
        ai_layout.addRow("API Key:", self.api_key_input)

        self.base_url_input = QLineEdit()
        self.base_url_input.setPlaceholderText("https://api.deepseek.com")
        ai_layout.addRow("Base URL:", self.base_url_input)

        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("moonshot-v1-8k")
        ai_layout.addRow("模型:", self.model_input)

        layout.addWidget(ai_group)

        # ---- 宠物配置 ----
        pet_group = QGroupBox("宠物配置")
        pet_layout = QFormLayout(pet_group)
        pet_layout.setSpacing(8)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("小橘")
        pet_layout.addRow("名字:", self.name_input)

        self.size_input = QSpinBox()
        self.size_input.setRange(64, 512)
        self.size_input.setSingleStep(16)
        pet_layout.addRow("尺寸 (像素):", self.size_input)

        self.interval_input = QSpinBox()
        self.interval_input.setRange(0, 3600)
        self.interval_input.setSingleStep(60)
        self.interval_input.setSuffix(" 秒")
        pet_layout.addRow("自动对话间隔:", self.interval_input)

        layout.addWidget(pet_group)

        # ---- 性格设定 ----
        personality_group = QGroupBox("性格设定（系统提示词）")
        personality_layout = QVBoxLayout(personality_group)

        self.personality_input = QTextEdit()
        self.personality_input.setPlaceholderText(
            "你是一只可爱的桌面宠物猫咪，性格活泼、粘人、会撒娇..."
        )
        self.personality_input.setMaximumHeight(120)
        personality_layout.addWidget(self.personality_input)

        layout.addWidget(personality_group)

        # ---- 按钮 ----
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.save_btn = QPushButton("保存")
        self.save_btn.setDefault(True)
        self.save_btn.clicked.connect(self._on_save)
        btn_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def _load_settings(self):
        """从数据库加载设置"""
        self.api_key_input.setText(self._db.get_setting("KIMI_API_KEY", ""))
        self.base_url_input.setText(
            self._db.get_setting("KIMI_BASE_URL", "https://api.deepseek.com")
        )
        self.model_input.setText(self._db.get_setting("KIMI_MODEL", "deepseek-chat"))
        self.name_input.setText(self._db.get_setting("PET_NAME", "小橘"))
        self.size_input.setValue(int(self._db.get_setting("PET_SIZE", "256")))
        self.interval_input.setValue(int(self._db.get_setting("AUTO_TALK_INTERVAL", "300")))
        self.personality_input.setText(self._db.get_setting("SYSTEM_PROMPT", ""))

    def _on_save(self):
        """保存设置到数据库和 .env"""
        try:
            self._db.set_setting("KIMI_API_KEY", self.api_key_input.text().strip())
            self._db.set_setting("KIMI_BASE_URL", self.base_url_input.text().strip())
            self._db.set_setting("KIMI_MODEL", self.model_input.text().strip())
            self._db.set_setting("PET_NAME", self.name_input.text().strip() or "小橘")
            self._db.set_setting("PET_SIZE", str(self.size_input.value()))
            self._db.set_setting("AUTO_TALK_INTERVAL", str(self.interval_input.value()))
            self._db.set_setting("SYSTEM_PROMPT", self.personality_input.toPlainText().strip())

            self._sync_to_env()

            logger.info("设置已保存")
            QMessageBox.information(self, "保存成功", "设置已保存，部分选项需重启后生效。")
            self.accept()
        except Exception as e:
            logger.error(f"保存设置失败: {e}")
            QMessageBox.critical(self, "保存失败", f"保存设置时出错: {e}")

    def _sync_to_env(self):
        """将数据库中的设置同步回 .env 文件"""
        env_path = self._db._db_path.parent.parent / ".env"
        settings = self._db.get_all_settings()

        lines = []
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

        output = []
        written_keys = set()

        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                output.append(line)
                continue
            if "=" in stripped:
                key = stripped.split("=", 1)[0]
                if key in settings:
                    output.append(f"{key}={settings[key]}\n")
                    written_keys.add(key)
                else:
                    output.append(line)

        for key, value in settings.items():
            if key not in written_keys:
                output.append(f"{key}={value}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(output)

        logger.info(f".env 文件已更新: {env_path}")
