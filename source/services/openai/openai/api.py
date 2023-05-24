import json

import openai
from fastapi import APIRouter, Request, Depends

from services.openai.openai import service
from services.openai.openai.dependencies import verify_api_key
from services.openai.openai.settings import settings

if settings.OPENAI_PROXY:
    openai.proxy = settings.OPENAI_PROXY
router_openai = APIRouter()


@router_openai.post(
    '/chat/completions',
    description='发送chat_completion消息',
)
async def create_chat_completion(
        request: Request,
        api_key: str = Depends(verify_api_key)
):
    items = json.loads(await request.body())
    return await service.save_and_post_chat(items, api_key)


@router_openai.post(
    '/completions',
    description='发送completions消息',
)
async def create_completions(
        request: Request,
        api_key: str = Depends(verify_api_key)
):
    items = json.loads(await request.body())
    return await service.post_completions(items, api_key)


@router_openai.post(
    '/embeddings',
    description='发送embeddings消息',
)
async def create_embeddings(
        request: Request,
        api_key: str = Depends(verify_api_key)
):
    items = json.loads(await request.body())
    return await service.post_embeddings(items, api_key)


@router_openai.get(
    '/health',
    description='健康查询',
)
async def get_health(request: Request):
    return {"result": "ok"}
