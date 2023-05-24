from typing import Optional, Dict

from pydantic import BaseModel


class MessageHeaderReq(BaseModel):
    event_type: Optional[str]
    event_id: Optional[str]
    create_time: Optional[str]
    token: Optional[str]
    app_id: Optional[str]
    tenant_key: Optional[str]


class MessageSenderIdReq(BaseModel):
    open_id: Optional[str]
    union_id: Optional[str]
    user_id: Optional[str]


class MessageSenderReq(BaseModel):
    sender_id: MessageSenderIdReq
    sender_type: Optional[str]
    tenant_key: Optional[str]


class MessageContentReq(BaseModel):
    message_id: Optional[str]
    root_id: Optional[str]
    parent_id: Optional[str]
    create_time: Optional[str]
    chat_id: Optional[str]
    chat_type: Optional[str]
    message_type: Optional[str]
    content: Optional[str]
    mentions: Optional[Dict]


class MessageEventReq(BaseModel):
    sender: MessageSenderReq
    message: MessageContentReq


class MessageReceiveReq(BaseModel):
    header: MessageHeaderReq
    event: MessageEventReq
