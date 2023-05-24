import json

from fastapi import APIRouter, Request
from services.auth.auth import service as auth_service
from services.auth.message import service
from services.auth.message.serializers import MessageReceiveReq

router_message = APIRouter()


@router_message.post(
    '/receive',
    description='接受飞书用户向机器人发送的消息',
)
async def get_message_receive(request: Request):
    """
    接受飞书用户向机器人发送的消息
    """

    # 初始化信息验证，只在第一次验证有效
    json_data = await request.json()
    if "challenge" in json_data:
        return {"challenge": json_data.get("challenge")}

    # 飞书消息体
    message = MessageReceiveReq(**json_data)

    # 验证消息内容
    if service.verify_message(message.event.message.content) == "help":
        await service.send_help_message(message.event.sender.sender_id.open_id, message.event.message.message_id)
    elif service.verify_message(message.event.message.content) == "other":
        await service.send_help_message(
            open_id=message.event.sender.sender_id.open_id,
            message_id=message.event.message.message_id,
            reply=True
        )
    elif service.verify_message(message.event.message.content) == "key":
        days = service.verify_message_days(message.event.message.content)
        user = await service.get_user_info(message.event.sender.sender_id.open_id, message.event.message.message_id)
        access_token = await auth_service.save_user_generate_token(user.dict(), days)
        await service.send_token_message(
            open_id=message.event.sender.sender_id.open_id,
            access_token=access_token,
            days=days,
            message_id=message.event.message.message_id
        )
    elif service.verify_message(message.event.message.content) == "select":
        tokens_list = await service.get_user_tokens(message.event.sender.sender_id.open_id)
        await service.send_select_message(
            open_id=message.event.sender.sender_id.open_id,
            tokens_list=tokens_list,
            message_id=message.event.message.message_id
        )

    return {"result": "ok"}
