import asyncio
import json
import logging
from datetime import timedelta, datetime
from typing import Union
import time

import aiohttp
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from starlette import status

from basic.common.log import logger
from services.auth.util.settings import settings

SECRET_KEY = "b37ffaedca99665111be4a30ec586efbcc05d5373f4869d29b13df003c04721c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 10
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="")
service_cache = dict()


def create_access_token(data: dict, expires_delta: Union[int, None] = None):
    """
    创建jwt token
    :param data:
    :param expires_delta: 时间
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(days=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decode_access_token(token: str = Depends(oauth2_scheme)):
    """
    解码jwt token并验证是否过期
    :param token: jwt token
    :return: open_id
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="app_key 认证失败，请从飞书获取认证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    expire_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="app_key 认证过期，请从飞书重新获取",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(payload)
        open_id: str = payload.get("sub")
        if not open_id:
            print(1)
            raise credentials_exception
        exp = payload.get("exp")
        if exp < int(datetime.utcnow().timestamp()):
            print(2)
            raise expire_exception
    except JWTError:
        raise credentials_exception
    return open_id


async def get_tenant_access_token():
    """
    获得飞书鉴权凭证 鉴权凭证会三十分钟过期
    :return: 鉴权凭证
    """
    if service_cache.get("tenant_access_token", None) and time.time() < service_cache.get(
            "tenant_access_token_expire", 0):
        return service_cache["tenant_access_token"]

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    req = {
        "app_id": settings.APP_ID,
        "app_secret": settings.APP_SECRET,
    }
    headers = {
        'Content-Type': "application/json; charset=utf-8"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=json.dumps(req)) as response:
            response = await response.json()
            print(response)
            if response['code'] != 0:
                logger.error(response['msg'])
                raise HTTPException(status_code=400, detail=response['msg'])

    service_cache["tenant_access_token_expire"] = time.time() + response['expire']
    service_cache["tenant_access_token"] = response["tenant_access_token"]
    return service_cache["tenant_access_token"]
