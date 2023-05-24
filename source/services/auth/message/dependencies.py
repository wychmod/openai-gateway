from fastapi import HTTPException
from starlette import status

from basic.common.log import logger
from services.auth.message.serializers import MessageReceiveReq


async def verify_event_type(message: MessageReceiveReq):
    """
    验证飞书消息事件类型
    :param message: 飞书消息体
    """
    if message.header.event_type != "im.message.receive_v1":
        logger.error(f"飞书消息推送失败，没有这种功能")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="飞书消息推送失败，没有这种功能")
