"""SQLite 数据库管理器 - 持久化对话历史和用户配置"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from utils.logger import setup_logger

logger = setup_logger()

DB_PATH = Path(__file__).parent.parent / "data" / "pet_data.db"


@dataclass
class ChatRecord:
    """对话记录"""

    role: str
    content: str
    created_at: str


class DBManager:
    """SQLite 数据库管理器"""

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    # ---- 初始化 ----

    def _init_db(self):
        """创建表结构"""
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS pet_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            logger.info(f"数据库已初始化: {self._db_path}")

    # ---- 对话历史 ----

    def save_chat(self, role: str, content: str):
        """保存一条对话记录"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "INSERT INTO chat_history (role, content, created_at) VALUES (?, ?, ?)",
                (role, content, datetime.now().isoformat()),
            )
            logger.debug(f"保存对话记录: role={role}")

    def load_chat_history(self, limit: int = 40) -> List[ChatRecord]:
        """加载最近 N 条对话记录"""
        with sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT role, content, created_at FROM chat_history ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            # 按时间正序返回
            return [ChatRecord(**dict(r)) for r in reversed(rows)]

    def clear_chat_history(self):
        """清空对话历史"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("DELETE FROM chat_history")
            logger.info("对话历史已清空")

    # ---- 应用设置 ----

    def set_setting(self, key: str, value: str):
        """保存设置项"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """INSERT INTO app_settings (key, value, updated_at)
                   VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET
                   value=excluded.value, updated_at=excluded.updated_at""",
                (key, value, datetime.now().isoformat()),
            )

    def get_setting(self, key: str, default: str = "") -> str:
        """读取设置项"""
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT value FROM app_settings WHERE key = ?", (key,)
            ).fetchone()
            return row[0] if row else default

    def get_all_settings(self) -> dict:
        """读取所有设置"""
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute("SELECT key, value FROM app_settings").fetchall()
            return {k: v for k, v in rows}

    # ---- 宠物状态 ----

    def set_state(self, key: str, value: str):
        """保存宠物状态"""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """INSERT INTO pet_state (key, value, updated_at)
                   VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET
                   value=excluded.value, updated_at=excluded.updated_at""",
                (key, value, datetime.now().isoformat()),
            )

    def get_state(self, key: str, default: str = "") -> str:
        """读取宠物状态"""
        with sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT value FROM pet_state WHERE key = ?", (key,)
            ).fetchone()
            return row[0] if row else default
