
from datetime import datetime

import ormar

from services.auth.util.initdb import DB, META


class DateModel(ormar.Model):
    class Meta:
        abstract = True

    created_at: datetime = ormar.DateTime(default=datetime.now)
    updated_at: datetime = ormar.DateTime(default=datetime.now)


class Conversation(DateModel):
    class Meta:
        tablename: str = "openai_conversation"
        database = DB
        metadata = META

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    conversation_id: str = ormar.String(max_length=128, unique=True, comment='会话id')
    open_id: str = ormar.String(max_length=200, comment='使用人openid')
    title: str = ormar.String(max_length=200, nullable=True, comment='会话题目')


class ChatCompletionMessage(DateModel):
    class Meta:
        tablename: str = "openai_chat_completion"
        database = DB
        metadata = META

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    message_id: str = ormar.String(max_length=128, unique=True, comment='消息id')
    conversation_id: str = ormar.String(max_length=128, index=True, comment='会话id')
    model: str = ormar.String(max_length=128, comment='模型')
    role: str = ormar.String(max_length=128, comment='角色')
    content: str = ormar.Text(comment='内容')
    name: str = ormar.String(max_length=128, nullable=True, default=None, comment='名字')
    parent: str = ormar.String(max_length=128, nullable=True, default=None, comment='父节点对话id')
    top_p: float = ormar.Float(default=1, comment='top_p')
    temperature: float = ormar.Float(default=1, comment='temperature')
    stream: bool = ormar.Boolean(default=False, comment='流式返回')

    def __repr__(self):
        return f'{self.role}_{self.content}'

    def __str__(self):
        return f'{self.role}_{self.content}'


class CompletionMessage(DateModel):
    class Meta:
        tablename: str = "openai_completion"
        database = DB
        metadata = META

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    open_id: str = ormar.String(max_length=200, index=True, comment='使用人openid')
    message_id: str = ormar.String(max_length=128, unique=True, comment='消息id')
    model: str = ormar.String(max_length=128, comment='模型')
    prompt: str = ormar.Text(comment='提示')
    content: str = ormar.Text(comment='内容')
    max_tokens: int = ormar.Integer(default=16, comment='最大消耗token数')
    temperature: float = ormar.Float(default=1, comment='temperature')
    top_p: float = ormar.Float(default=1, comment='top_p')
    stop: str = ormar.String(max_length=128, default="\\n", comment='停止符')
    stream: bool = ormar.Boolean(default=False, comment='流式返回')
    logprobs: int = ormar.Integer(default=None, nullable=True, comment='logprobs')

    def __repr__(self):
        return f'{self.open_id}_{self.prompt}'

    def __str__(self):
        return f'{self.open_id}_{self.prompt}'


class EmbeddingsMessage(DateModel):
    class Meta:
        tablename: str = "openai_embeddings"
        database = DB
        metadata = META

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    open_id: str = ormar.String(max_length=200, index=True, comment='使用人openid')
    message_id: str = ormar.String(max_length=128, unique=True, comment='消息id')
    model: str = ormar.String(max_length=128, comment='模型')
    input: str = ormar.Text(comment='输入')
    embedding: str = ormar.Text(comment='embedding')

    def __repr__(self):
        return f'{self.open_id}_{self.input}'

    def __str__(self):
        return f'{self.open_id}_{self.input}'



