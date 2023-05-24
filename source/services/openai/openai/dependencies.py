from typing import Union

from fastapi import HTTPException, Header
from starlette import status

from basic.common.log import logger
from services.openai.openai.settings import settings


async def verify_api_key(authorization: Union[str, None] = Header(default=None)):
    """
    验证是否有api_key
    """
    if not authorization:
        logger.info(f"The server is missing an API key")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The server is missing an API key. Please contact developer")
    return authorization.split()[-1]
