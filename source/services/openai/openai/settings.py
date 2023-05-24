from typing import Union
from pydantic import BaseSettings


class Settings(BaseSettings):
    OPENAI_PROXY: Union[str, None]


settings = Settings()
