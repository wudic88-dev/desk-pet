from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""

    # AI API (兼容 OpenAI 格式，默认 DeepSeek)
    kimi_api_key: str = Field(default="", alias="KIMI_API_KEY")
    kimi_model: str = Field(default="deepseek-chat", alias="KIMI_MODEL")
    kimi_base_url: str = Field(default="https://api.deepseek.com", alias="KIMI_BASE_URL")

    # 宠物配置
    pet_name: str = Field(default="小橘", alias="PET_NAME")
    pet_size: int = Field(default=256, alias="PET_SIZE")

    # 行为配置
    auto_talk_interval: int = Field(default=300, alias="AUTO_TALK_INTERVAL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
