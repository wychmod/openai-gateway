import uuid
from typing import List

from fastapi import APIRouter, Depends, Request, BackgroundTasks

from services.auth.auth import service
from services.auth.auth.dependencies import verify_auth_code, verify_OPENAI_API_KEY
from services.auth.auth.serializers import UserTokensRes
from services.auth.util.utils import decode_access_token

router_auth = APIRouter()
router_openai = APIRouter()


@router_auth.get(
    '/callback/openai',
    description='通过回调获得的登陆授权码来获得access_token',
)
async def get_access_token(code: str = Depends(verify_auth_code)):
    response = await service.get_access_token(code)
    user = await service.get_user_info(response.get('access_token'))
    token = await service.save_user_generate_token(user.dict())

    return {"access_token": token, "token_type": "bearer"}


@router_auth.get(
    '/tokens',
    description='查询用户使用tokens',
    response_model=List[UserTokensRes]
)
async def list_user_tokens():
    return await service.list_user_tokens()


@router_auth.get(
    '/health',
    description='健康查询',
)
async def get_health():
    return {"result": "ok"}


@router_openai.post(
    '/chat/completions',
    description='发送chat_completion消息',
    dependencies=[Depends(verify_OPENAI_API_KEY)]
)
async def create_chat_completion(
        request: Request,
        background_tasks: BackgroundTasks,
        open_id: str = Depends(decode_access_token)
):
    background_tasks.add_task(service.send_chat_question_mq, request, open_id)
    response = await service.save_and_post_chat(request, background_tasks, open_id)
    background_tasks.add_task(service.send_chat_answer_mq, request, response, open_id)
    return response


@router_openai.post(
    '/completions',
    description='发送completions消息',
    dependencies=[Depends(verify_OPENAI_API_KEY)]
)
async def create_completions(
        request: Request,
        background_tasks: BackgroundTasks,
        open_id: str = Depends(decode_access_token)
):
    response = await service.post_completions(request, background_tasks, open_id)
    background_tasks.add_task(service.send_complete_mq, request, response, open_id)
    return response


@router_openai.post(
    '/embeddings',
    description='发送embeddings消息',
    dependencies=[Depends(verify_OPENAI_API_KEY)]
)
async def create_embeddings(
        request: Request,
        background_tasks: BackgroundTasks,
        open_id: str = Depends(decode_access_token)
):
    response = await service.post_embeddings(request, background_tasks, open_id)
    background_tasks.add_task(service.send_embeddings_mq, request, response, open_id)
    return response
