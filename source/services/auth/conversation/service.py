from fastapi import HTTPException
from fastapi_pagination.ext.ormar import paginate
from starlette import status

from services.auth.conversation.model import EmbeddingsMessage, CompletionMessage, ChatCompletionMessage, Conversation


async def get_embedding_by_id(message_id: str):
    """
    根据message_id查询embedding
    """
    embeddings = await EmbeddingsMessage.objects.get_or_none(message_id=message_id)
    if not embeddings:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Embeddings not found")
    return embeddings


async def get_embeddings():
    """
    分页查询embeddings
    """
    return await paginate(EmbeddingsMessage.objects)


async def get_completion_by_id(message_id):
    """
    根据message_id查询completion
    """
    completion = await CompletionMessage.objects.get_or_none(message_id=message_id)
    if not completion:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="completion not found")
    return completion


async def get_completions():
    """
    分页查询completion
    """
    return await paginate(CompletionMessage.objects)


async def get_chat_by_id(message_id):
    """
    根据message_id查询chat
    """
    chat = await ChatCompletionMessage.objects.get_or_none(message_id=message_id)
    if not chat:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="completion not found")
    return chat


async def get_conversations():
    """
    分页查询conversation
    """
    return await paginate(Conversation.objects)


async def get_conversation_by_id(message_id):
    """
    根据message_id查询conversation，以及该conversation下的所有chat
    """
    conversation = await Conversation.objects.get_or_none(conversation_id=message_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="conversation not found")
    conversation_dict = conversation.dict()
    chats = await ChatCompletionMessage.objects.filter(conversation_id=message_id).all()
    chats_dict = {chat.message_id: chat.dict() for chat in chats}
    parent_dict = {}
    for chat in chats:
        if chat.parent:
            parent = parent_dict.get(chat.parent, [])
            parent.append(chat.message_id)
            parent_dict[chat.parent] = parent
    for key, val in parent_dict.items():
        chats_dict[key]["children"] = val
    conversation_dict['mapping'] = chats_dict
    return conversation_dict
