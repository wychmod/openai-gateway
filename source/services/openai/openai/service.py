import openai
from fastapi import HTTPException
from starlette import status

from basic.common.log import logger


async def save_and_post_chat(items: dict, api_key: str):
    """
    调用chat_completion方法
    :param items: chat_completion方法的参数
    :param api_key: openai使用的api_key
    """
    try:
        logger.info(f"use api_key:{api_key}")
        openai.api_key = api_key
        res = openai.ChatCompletion.create(**items)
        if res:
            logger.info(f"output:{res}")
            return res
    except openai.error.RateLimitError as e:
        return {"error": e.error}
    except Exception as e:
        logger.info(f"Exception:{e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e)


async def post_completions(items: dict, api_key: str):
    """
    调用completions方法
    :param items: completions方法的参数
    :param api_key: openai使用的api_key
    """
    try:
        logger.info(f"use api_key:{api_key}")
        openai.api_key = api_key
        res = openai.Completion.create(**items)
        if res:
            logger.info(f"output:{res}")
            return res
    except openai.error.RateLimitError as e:
        return {"error": e.error}
    except Exception as e:
        logger.info(f"Exception:{e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e)


async def post_embeddings(items: dict, api_key: str):
    """
    调用embeddings方法
    :param items: embeddings方法的参数
    :param api_key: openai使用的api_key
    """
    try:
        logger.info(f"use api_key:{api_key}")
        openai.api_key = api_key
        res = openai.Embedding.create(**items)
        if res:
            logger.info(f"output:{res}")
            return res
    except openai.error.RateLimitError as e:
        logger.info(f"Exception:{e.error}")
        return {"error": e.error}
    except Exception as e:
        logger.info(f"Exception:{e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=e)
