from fastapi import APIRouter
from fastapi_pagination import LimitOffsetPage
from fastapi_pagination.ext.ormar import paginate
from services.auth.conversation import service
from services.auth.conversation.serializers import EmbeddingsRes, CompletionSimpleRes, CompletionDetailRes, \
    ConversationListRes, ConversationDetailRes

router_conversation = APIRouter()


@router_conversation.get(
    '/chats/{message_id}',
    description='获取单条chat_completion会话的详细信息',
    response_model=ConversationDetailRes
)
async def get_conversation_by_id(message_id: str):
    return await service.get_conversation_by_id(message_id)


@router_conversation.get(
    '/chats',
    description='获取chat_completion会话的分页信息',
    response_model=LimitOffsetPage[ConversationListRes]
)
async def get_conversations():
    return await service.get_conversations()


@router_conversation.get(
    '/completions/{message_id}',
    description='获取completions信息',
    response_model=CompletionDetailRes
)
async def get_completion_by_id(message_id: str):
    return await service.get_completion_by_id(message_id)


@router_conversation.get(
    '/completions',
    description='获取completions信息',
    response_model=LimitOffsetPage[CompletionSimpleRes]
)
async def get_completion_by_id():
    return await service.get_completions()


@router_conversation.get(
    '/embeddings/{message_id}',
    description='获取embeddings信息',
    response_model=EmbeddingsRes
)
async def get_embedding_by_id(message_id: str):
    return await service.get_embedding_by_id(message_id)


@router_conversation.get(
    '/embeddings',
    description='获取embeddings分页信息',
    response_model=LimitOffsetPage[EmbeddingsRes]
)
async def get_embeddings():
    return await service.get_embeddings()
