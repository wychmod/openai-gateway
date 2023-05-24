import re
from typing import List, Union

from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "123456"
    DB_HOST: str = "127.0.0.1"
    DB_PORT: str = "5432"
    DB_NAME: str = "openai"
    APP_ID: str = ""
    APP_SECRET: str = ""
    AUTH_SERVICE_URL: str = "http://127.0.0.1:8000"
    OPENAI_API_KEY: Union[str, List, None] = None
    OPENAI_PROXY: Union[str, None]
    LOAD_BALANCER_RULE: str = "random"
    OPENAI_URL: str = ""
    RETRY_COUNT: int = 3
    RETRY_TIME: int = 1

    ROCKETMQ_NAME_SERVER: str = "120.48.73.227:9876"

    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_USERNAME: str = ""
    REDIS_PASSWORD: str = ""

    @validator("LOAD_BALANCER_RULE")
    def validate_balancer_rule(cls, LOAD_BALANCER_RULE: str):

        return LOAD_BALANCER_RULE.lower()

    @validator("OPENAI_API_KEY")
    def validate_api_key(cls, OPENAI_API_KEY: str):
        if not OPENAI_API_KEY:
            return None
        return [s.strip() for s in re.split('[,，]', OPENAI_API_KEY)]


settings = Settings()
