import json
import time

from rocketmq.client import PushConsumer, ConsumeStatus
from sqlalchemy.orm import Session

from basic.common.log import logger
from services.message.message.model import EmbeddingsMessage, CompletionMessage, Conversation, ChatCompletionMessage
from services.message.util.initdb import get_db
from services.message.util.settings import settings


def receive_embeddings(msg):
    """
    接收embeddings消息保存入数据库
    :param msg: rocketmq消息体
    """
    embeddings = json.loads(msg.body)
    try:
        db = get_db()
        db.add(EmbeddingsMessage(**embeddings))
        db.commit()
        logger.info(embeddings)
        return ConsumeStatus.CONSUME_SUCCESS
    except Exception as e:
        logger.error(e)
        return ConsumeStatus.RECONSUME_LATER


def receive_chat(msg):
    """
    接收chat_complete消息保存入数据库
    :param msg: rocketmq消息体
    """
    chat = json.loads(msg.body)
    try:
        db: Session = get_db()
        conversation = db.query(Conversation).filter(
            Conversation.conversation_id == chat.get("conversation_id")).first()
        if not conversation:
            conversation = Conversation(
                conversation_id=chat.get("conversation_id"),
                open_id=chat.get("open_id"),
                title=chat.get("title"),
            )
            db.add(conversation)
            db.commit()
        chatCompletionMessage = ChatCompletionMessage(
            message_id=chat.get("message_id"),
            conversation_id=chat.get("conversation_id"),
            model=chat.get("model"),
            role=chat.get("role"),
            content=chat.get("content"),
            name=chat.get("name"),
            parent=chat.get("parent"),
            top_p=chat.get("top_p"),
            temperature=chat.get("temperature"),
            stream=chat.get("stream"),
        )
        db.add(chatCompletionMessage)
        db.commit()
        logger.info(chat)
        return ConsumeStatus.CONSUME_SUCCESS
    except Exception as e:
        logger.error(e)
        return ConsumeStatus.RECONSUME_LATER


def receive_complete(msg):
    """
    接收complete消息保存入数据库
    :param msg: rocketmq消息体
    """
    complete = json.loads(msg.body)
    try:
        db = get_db()
        db.add(CompletionMessage(**complete))
        db.commit()
        logger.info(complete)
        return ConsumeStatus.CONSUME_SUCCESS
    except Exception as e:
        logger.error(e)
        return ConsumeStatus.RECONSUME_LATER


def mq_consumer():
    """
    启动消息队列消费者, 订阅了三个topic
    """
    chat_consumer = PushConsumer('chat_consumer')
    chat_consumer.set_name_server_address(settings.ROCKETMQ_NAME_SERVER)
    chat_consumer.subscribe('openai_chat', receive_chat)
    chat_consumer.start()

    embeddings_consumer = PushConsumer('embeddings_consumer')
    embeddings_consumer.set_name_server_address(settings.ROCKETMQ_NAME_SERVER)
    embeddings_consumer.subscribe('openai_embeddings', receive_embeddings)
    embeddings_consumer.start()

    complete_consumer = PushConsumer('complete_consumer')
    complete_consumer.set_name_server_address(settings.ROCKETMQ_NAME_SERVER)
    complete_consumer.subscribe('openai_complete', receive_complete)
    complete_consumer.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        embeddings_consumer.shutdown()
        complete_consumer.shutdown()
        chat_consumer.shutdown()


if __name__ == '__main__':
    # 消费者
    mq_consumer()
