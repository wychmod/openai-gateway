import re
from typing import List, Union

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """
    项目配置
    """
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "123456"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: str = "5432"
    DB_NAME: str = "openai"

    ROCKETMQ_NAME_SERVER: str = "120.48.73.227:9876"


settings = Settings()
