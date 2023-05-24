from typing import Optional
from fastapi import HTTPException
from starlette import status

from basic.common.log import logger
from services.auth.util.settings import settings


async def verify_auth_code(code: Optional[str]):
    """
    验证飞书身份认证授权码
    :param code: 授权码
    """
    if not code:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="飞书身份认证失败，没有收到授权码")
    return code


async def verify_OPENAI_API_KEY():
    """
    验证OPENAI_API_KEY
    :return:
    """
    if not settings.OPENAI_API_KEY:
        logger.info(f"The server is missing an available API key")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="The server is missing an available API key. Please contact developer")
