import json
from typing import List

import aiohttp
import backoff
from fastapi import HTTPException
from starlette import status

from basic.common.log import logger
from services.auth.auth.model import User
from services.auth.auth.serializers import UserDetailRes
from services.auth.util.utils import get_tenant_access_token


def verify_message(content: str):
    """
    验证消息类型
    :return: 消息类型
    """
    if content.find("帮助") != -1 or content.find("help") != -1:
        return "help"
    elif content.find("key") != -1 and content.find("获取") != -1:
        return "key"
    elif content.find("查询") != -1 and content.find("用量") != -1:
        return "select"
    return "other"


def verify_message_days(content: str):
    """
    验证消息中的天数
    :param content: 消息体
    :return: 消息体中的天数
    """
    if content.find("天") == -1:
        return 10
    return int(content[content.find("y")+1:content.find("天")])


async def get_user_info(open_id: str, message_id: str):
    """
    获取飞书用户信息
    :param open_id: 通过open_id获取用户信息
    :param message_id: 通过message_id消息去重
    :return:
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://open.feishu.cn/open-apis/contact/v3/users/{open_id}?department_id_type=open_department_id" \
              f"&user_id_type=open_id"
        headers = {
            'Authorization': "Bearer " + await get_tenant_access_token(),
        }
        async with session.get(url, headers=headers) as response:
            response = await response.json()
            if response.get('code') != 0:
                await send_help_message(open_id, message_id, reply=True)
                raise Exception(response.get('msg'))
            user = response.get("data").get("user")
            return UserDetailRes(**user)


@backoff.on_exception(backoff.constant, HTTPException, max_tries=3, interval=1)
async def send_message(open_id: str, msg_type: str, content: str, message_id: str):
    """
    发送消息基本方法
    :param message_id: 消息唯一id
    :param open_id: 消息的用户id或群id
    :param msg_type: 消息的类型
    :param content: 消息的内容
    :return:
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
        headers = {
            'Authorization': "Bearer " + await get_tenant_access_token(),
            'Content-Type': "application/json; charset=utf-8"
        }
        req = {
            "receive_id": open_id,
            "msg_type": msg_type,
            "content": content,
            "uuid": message_id
        }
        async with session.post(url, headers=headers, data=json.dumps(req)) as response:
            response = await response.json()
            if response.get('code') != 0:
                logger.error(response['msg'])
                await send_help_message(open_id, message_id, reply=True)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=response.get('msg'))
            return response


async def send_help_message(open_id: str, message_id: str, reply: bool = False):
    """
    发送帮助消息
    :return:
    """
    content = {
        "zh_cn": {
            "title": "抱歉我没有理解你的消息" if reply else "欢迎使用应用机器人" + "，您可以通过以下方式获取帮助：",
            "content": [
                [
                    {
                        "tag": "text",
                        "text": "1. 输入\"",
                        "style": []

                    },
                    {
                        "tag": "text",
                        "text": "获取key",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": "\"获取openai的access key, 有效期为10天。\n",
                        "style": []
                    },
                ],
                [
                    {
                        "tag": "text",
                        "text": "2. 输入\"",
                        "style": []

                    },
                    {
                        "tag": "text",
                        "text": "获取key n天",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": "\"获取openai的access key, 有效期为n天。\n",
                        "style": []
                    }
                ],
                [
                    {
                        "tag": "text",
                        "text": "3. 输入\"",
                        "style": []

                    },
                    {
                        "tag": "text",
                        "text": "帮助",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": "\"或\"",
                        "style": []
                    },
                    {
                        "tag": "text",
                        "text": "help",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": "\"获取帮助信息。\n",
                        "style": []
                    }
                ],
                [
                    {
                        "tag": "text",
                        "text": "4. 输入\"",
                        "style": []

                    },
                    {
                        "tag": "text",
                        "text": "查询用量",
                        "style": ["bold"]
                    },
                    {
                        "tag": "text",
                        "text": "\"获取当前账户消耗的openai的tokens总量。\n",
                        "style": []
                    }
                ]
            ]
        }
    }
    await send_message(open_id, "post", json.dumps(content), message_id)


async def send_token_message(open_id: str, access_token: str, days: int, message_id: str):
    """
    发送token消息
    :return:
    """
    content = {
        "zh_cn": {
            "title": "下面是属于你的access token",
            "content": [
                [
                    {
                        "tag": "text",
                        "text": f"{access_token}\n",
                        "style": []
                    }
                ],
                [
                    {
                        "tag": "text",
                        "text": f"ps: 请将access token配置到openai.api_key中。有效期为{days}天。\n",
                        "style": []

                    }
                ],
                [
                    {
                        "tag": "text",
                        "text": f"详细内容：请查看",
                        "style": ["bold"]

                    },
                    {
                        "tag": "a",
                        "href": "https://digital-brain.feishu.cn/docx/CmgTdF3PKoodOJx0fAXcncUInNf",
                        "text": "openai网关使用说明",
                        "style": ["bold", "italic"]
                    }
                ]

            ]
        }
    }
    await send_message(open_id, "post", json.dumps(content), message_id)


async def send_select_message(open_id: str, tokens_list: List, message_id: str):
    """
    发送查询token消耗的信息
    :return:
    """
    content = {
        "zh_cn": {
            "title": "当前消耗tokens数量为：",
            "content": [
                [
                    {
                        "tag": "text",
                        "text": f"{name}消耗了{tokens}个openai的tokens\n",
                        "style": ["bold"]
                    }
                    for name, tokens in tokens_list
                ]
            ]
        }
    }
    await send_message(open_id, "post", json.dumps(content), message_id)


async def get_user_tokens(open_id):
    """
    查询用户消耗tokens数，如果是管理员则查询所有用户
    :param open_id:
    :return:
    """
    if open_id in ["ou_e8ec2db2ea5e7d5f186142f070d9b904", "ou_49b6c94e13d9b3821e1dc126243f173e"]:
        user = await User.objects.all()
    else:
        user = await User.objects.filter(open_id=open_id).all()
    return [(u.name, u.tokens) for u in user]
