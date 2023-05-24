import asyncio
import json
import uuid
import hashlib
from typing import Dict, List
import backoff
import aiohttp
from fastapi import HTTPException, Request
from rocketmq.client import Message
from starlette import status

from basic.common.exception import BackoffException
from services.auth.util.initdb import DB, producer, redis_conn
from basic.common.log import logger
from basic.utils.load_balance import api_key_server
from services.auth.util.settings import settings
from services.auth.util.utils import create_access_token
from services.auth.auth.model import User
from services.auth.auth.serializers import AccessTokenReq, UserDetailRes


async def get_access_token(code: str):
    """
    获得飞书access_token
    :param code: 飞书认证后的code
    :return:
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://passport.feishu.cn/suite/passport/oauth/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        form_data = aiohttp.FormData(fields=AccessTokenReq(code=code).dict())
        async with session.post(url, headers=headers, data=form_data) as response:
            response = await response.json()
            if response.get('error'):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail=response.get('error_description', response['error']))
            return response


async def get_user_info(access_token: str):
    """
    通过access_token获取用户信息
    :param access_token:飞书用户access_token
    :return:用户信息
    """
    async with aiohttp.ClientSession() as session:
        url = f"https://passport.feishu.cn/suite/passport/oauth/userinfo"
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        async with session.get(url, headers=headers) as response:
            response = await response.json()
            user = UserDetailRes(**response)
            return user


async def save_user_generate_token(user_info: dict, days: int = 10):
    """
    保存用户信息并生成jwt token
    """
    access_token = create_access_token(
        data={"sub": user_info.get("open_id")},
        expires_delta=days
    )
    user_info["access_token"] = access_token

    user = await User.objects.get_or_none(open_id=user_info.get('open_id'))
    if not user:
        await User.objects.create(**user_info)
    else:
        await user.update(access_token=access_token)

    return access_token


async def update_user_tokens(openid: str, tokens: int):
    """
    更新用户的tokens使用量
    :param openid: 用户的openid
    :param tokens: 用户使用tokens
    """
    sql = (
        f"UPDATE openai_user SET tokens = tokens + {tokens} WHERE open_id = \'{openid}\'"
    )
    await DB.execute(sql)


async def list_user_tokens():
    """
    查询所有用户使用的tokens
    """
    return await User.objects.all()


def retrying_process(func):
    """
    整个重试流程的装饰器，因为不同函数都要经过这个重试流程，所以抽象出来
    """
    async def wrapper(request, background_tasks, open_id):
        items = await request.body()
        logger.info(f"input:{items}")
        api_key_set = set(api_key_server.servers)
        for _ in range(settings.RETRY_COUNT):

            if settings.LOAD_BALANCER_RULE == "random":
                api_key = await random_traversal(request, api_key_set)
            else:
                api_key = await api_key_server.get_server(request)

            logger.info(f"use api_key:{api_key}")
            res = await func(items, api_key)
            if error := res.get('error'):
                if error['type'] == "insufficient_quota":
                    logger.info(f"remove api_key:{api_key}")
                    settings.OPENAI_API_KEY.remove(api_key)
                await asyncio.sleep(settings.RETRY_TIME)
                logger.info(f"Exception:{error['message']}")
            else:
                logger.info(f"output:{res}")
                background_tasks.add_task(update_user_tokens, open_id, res['usage']['total_tokens'])
                return res

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='openai-gateway: Still unsuccessful after retrying')

    return wrapper


@retrying_process
async def save_and_post_chat(items, api_key: str):
    """
    发送chat_completions请求
    :param items: 请求参数
    :param api_key: openai的apikey
    :return:
    """
    async with aiohttp.ClientSession() as session:
        url = f"{settings.OPENAI_URL}/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': api_key
        }
        async with session.post(url, headers=headers, data=items) as response:
            response = await response.json()
            return response


@retrying_process
async def post_completions(items: dict, api_key: str):
    """
    发送completions请求
    :param items: 请求参数
    :param api_key: openai的apikey
    :return:
    """
    async with aiohttp.ClientSession() as session:
        url = f"{settings.OPENAI_URL}/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': api_key
        }
        async with session.post(url, headers=headers, data=items) as response:
            response = await response.json()
            return response


@retrying_process
async def post_embeddings(items: dict, api_key: str):
    """
    发送embeddings请求
    :param items: 请求参数
    :param api_key: openai的apikey
    :return:
    """
    async with aiohttp.ClientSession() as session:
        url = f"{settings.OPENAI_URL}/embeddings"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': api_key
        }
        async with session.post(url, headers=headers, data=items) as response:
            response = await response.json()
            return response


async def random_traversal(request, api_key_set: set):
    """
    随机遍历api_key
    """
    api_key = await api_key_server.get_server(request)
    while api_key_set and api_key not in api_key_set:
        api_key = await api_key_server.get_server(request)
    api_key_set.remove(api_key)
    print(api_key_set)
    return api_key


async def send_embeddings_mq(request: Request, response: Dict, open_id: str):
    """
    发送embeddings到mq
    """
    items: dict = await request.json()
    if not items.get("model") or not items.get("input") or not response.get("data"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="model and input is required or have not data")
    for index, embedding in enumerate(response["data"]):
        unique_message = str(uuid.uuid4())
        msg_body = {
            "open_id": open_id,
            "message_id": unique_message,
            "model": items.get("model"),
            "input": items.get("input")[index],
            "embedding": embedding.get("embedding")
        }
        await send_message_mq('openai_embeddings', unique_message, 'embeddings', msg_body)


async def send_complete_mq(request: Request, response: Dict, open_id: str):
    """
    发送complete到mq
    """
    items: dict = await request.json()
    if not items.get("model") or not response.get("choices"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="model is required or have not data")
    for choice in response["choices"]:
        unique_message = str(uuid.uuid4())
        msg_body = {
            "open_id": open_id,
            "message_id": unique_message,
            "model": items.get("model"),
            "prompt": items.get("prompt"),
            "content": choice.get("text"),
            "max_tokens": items.get("max_tokens", 16),
            "temperature": items.get("temperature", 1),
            "top_p": items.get("top_p", 1),
            "stop": items.get("stop"),
            "stream": items.get("stream", False),
            "logprobs": choice.get("logprobs"),
        }
        await send_message_mq('openai_complete', unique_message, 'complete', msg_body)


def get_conversation_key(messages: List):
    """
    获取messages中的第一个问题来进行判断是否是同一个conversation
    """
    for message in messages:
        if message.get("role") == "system":
            continue
        elif message.get("role") == "user":
            return message.get("content")
    if len(messages) == 1:
        return messages[0].get("content")
    if len(messages) == 2:
        return messages[1].get("content")
    return messages[-1].get("content")


async def check_conversation(items: dict, open_id: str):
    """
    检查是否是同一个conversation
    """
    messages = items.get("messages")
    message_content = get_conversation_key(messages)
    conversation_key = hashlib.sha256(message_content.encode()).hexdigest()
    if not redis_conn.exists(conversation_key):
        # 1. save conversation to redis
        redis_message = {
            "conversation_id": str(uuid.uuid4()),
            "title": message_content,
            "open_id": open_id,
            "current_message": str(uuid.uuid4()),
        }
        redis_conn.hmset(conversation_key, redis_message)
        redis_conn.expire(conversation_key, 15 * 60)
        # 2. send system role message to mq
        if messages[0].get("role") == "system":
            msg_body = {
                "conversation_id": redis_message["conversation_id"],
                "open_id": open_id,
                "title": message_content,
                "message_id": redis_message["current_message"],
                "model": items.get("model"),
                "role": "system",
                "content": messages[0].get("content"),
                "name": messages[0].get("name"),
                "parent": None,
                "top_p": items.get("top_p", 1),
                "temperature": items.get("temperature", 1),
                "stream": items.get("stream", False),
            }
            await send_message_mq('openai_chat', redis_message["current_message"], 'chat', msg_body)
        else:
            redis_conn.hset(conversation_key, "current_message", "")
    return conversation_key


async def send_chat_question_mq(request: Request, open_id: str):
    """
    把chat问题发送到mq
    """
    items: dict = await request.json()
    if not items.get("model") or not items.get("messages"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="model and messages is required")
    conversation_key = await check_conversation(items, open_id)
    messages = items.get("messages")
    if messages[-1].get("role") == "system":
        return
    c_id, c_title, c_message = redis_conn.hmget(conversation_key, "conversation_id", "title", "current_message")
    msg_body = {
        "conversation_id": c_id,
        "open_id": open_id,
        "title": c_title,
        "message_id": str(uuid.uuid4()),
        "model": items.get("model"),
        "role": messages[-1].get("role"),
        "content": messages[-1].get("content"),
        "name": messages[-1].get("name"),
        "parent": c_message,
        "top_p": items.get("top_p", 1),
        "temperature": items.get("temperature", 1),
        "stream": items.get("stream", False),
    }
    await send_message_mq('openai_chat', msg_body["message_id"], 'chat', msg_body)
    redis_conn.hset(conversation_key, "current_message", msg_body["message_id"])
    redis_conn.expire(conversation_key, 15 * 60)


async def send_chat_answer_mq(request: Request, response: Dict, open_id: str):
    """
    把chat回答发送到mq
    """
    items: dict = await request.json()
    if not response.get("choices"):
        logger.error("没有答案返回")
        return
    conversation_key = await check_conversation(items, open_id)
    c_id, c_title, c_message = redis_conn.hmget(conversation_key, "conversation_id", "title", "current_message")
    # 如果生成多个答案取最后一个当下一个问题的parent
    unique_message = ""
    for choice in response["choices"]:
        message = choice.get("message")
        unique_message = str(uuid.uuid4())
        msg_body = {
            "conversation_id": c_id,
            "open_id": open_id,
            "title": c_title,
            "message_id": unique_message,
            "model": items.get("model"),
            "role": message.get("role"),
            "content": message.get("content"),
            "name": message.get("name"),
            "parent": c_message,
            "top_p": items.get("top_p", 1),
            "temperature": items.get("temperature", 1),
            "stream": items.get("stream", False),
        }
        await send_message_mq('openai_chat', unique_message, 'chat', msg_body)
    redis_conn.hset(conversation_key, "current_message", unique_message)
    redis_conn.expire(conversation_key, 15 * 60)


@backoff.on_exception(backoff.constant, BackoffException, max_tries=3, interval=1)
async def send_message_mq(topic: str, unique_message: str, tag: str, msg_body: dict):
    """
    发送消息到mq
    :param topic: mq topic
    :param unique_message: 唯一消息id
    :param tag: mq tag
    :param msg_body: mq 消息体
    :return:
    """
    msg = Message(topic)
    msg.set_keys(unique_message)
    msg.set_tags(tag)
    body = json.dumps(msg_body).encode('utf-8')
    msg.set_body(body)
    ret = producer.send_sync(msg)
    if ret.status != 0:
        logger.info(f"send message to mq failed")
        raise BackoffException(f"send message to mq failed")
