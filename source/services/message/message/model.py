
from sqlalchemy import func, Column, DateTime, Integer, String, Text, Float, Boolean, MetaData
from datetime import datetime

from services.message.util.initdb import engine, Base


class DateModel(Base):
    __abstract__ = True
    created_at: datetime = Column(DateTime, server_default=func.now(), comment='创建日期')
    updated_at: datetime = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新日期')


class Conversation(DateModel):
    __tablename__ = "openai_conversation"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id: str = Column(String(128), unique=True, comment='会话id')
    open_id: str = Column(String(200), comment='使用人openid')
    title: str = Column(String(200), comment='会话题目')


class ChatCompletionMessage(DateModel):
    __tablename__ = "openai_chat_completion"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    message_id: str = Column(String(128), unique=True, comment='消息id')
    conversation_id: str = Column(String(128), index=True, comment='会话id')
    model: str = Column(String(128), comment='模型')
    role: str = Column(String(128), comment='角色')
    content: str = Column(Text, comment='内容')
    name: str = Column(String(128), nullable=True, default=None, comment='名字')
    parent: str = Column(String(128), nullable=True, default=None, comment='父节点对话id')
    top_p: float = Column(Float, default=1, comment='top_p')
    temperature: float = Column(Float, default=1, comment='temperature')
    stream: bool = Column(Boolean, default=False, comment='流式返回')

    def __repr__(self):
        return f'{self.role}_{self.content}'

    def __str__(self):
        return f'{self.role}_{self.content}'


class CompletionMessage(DateModel):
    __tablename__ = "openai_completion"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    open_id: str = Column(String(200), index=True, comment='使用人openid')
    message_id: str = Column(String(128), unique=True, comment='消息id')
    model: str = Column(String(128), comment='模型')
    prompt: str = Column(Text, comment='提示')
    content: str = Column(Text, comment='内容')
    max_tokens: int = Column(Integer, default=16, comment='最大消耗token数')
    temperature: float = Column(Float, default=1, comment='temperature')
    top_p: float = Column(Float, default=1, comment='top_p')
    stop: str = Column(String(128), default="\\n", comment='停止符')
    stream: bool = Column(Boolean, default=False, comment='流式返回')
    logprobs: int = Column(Integer, default=None, nullable=True, comment='logprobs')

    def __repr__(self):
        return f'{self.open_id}_{self.prompt}'

    def __str__(self):
        return f'{self.open_id}_{self.prompt}'


class EmbeddingsMessage(DateModel):
    __tablename__ = "openai_embeddings"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    open_id: str = Column(String(200), index=True, comment='使用人openid')
    message_id: str = Column(String(128), unique=True, comment='消息id')
    model: str = Column(String(128), comment='模型')
    input: str = Column(Text, comment='输入')
    embedding: str = Column(Text, comment='embedding')

    def __repr__(self):
        return f'{self.open_id}_{self.input}'

    def __str__(self):
        return f'{self.open_id}_{self.input}'


Base.metadata.create_all(bind=engine)

