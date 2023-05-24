import databases
import sqlalchemy
import redis
from services.auth.util.settings import settings
from rocketmq.client import Producer, Message

# 消息队列生产者连接
producer = Producer('openai_producer')
producer.set_name_server_address(settings.ROCKETMQ_NAME_SERVER)

# 数据库连接
DB_CONN = f'{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/' \
          f'{settings.DB_NAME}'

DB_POSTGRESQL_CONN = f'postgresql://{DB_CONN}'

DB = databases.Database(DB_POSTGRESQL_CONN)
META = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DB_POSTGRESQL_CONN)

# redis连接
redis_conn = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    username=settings.REDIS_USERNAME,
    password=settings.REDIS_PASSWORD,
    db=settings.REDIS_DB,
    decode_responses=True
)


async def startup_event() -> None:
    if not DB.is_connected:
        await DB.connect()
        META.create_all(engine)

    producer.start()


async def shutdown_event() -> None:
    if DB.is_connected:
        await DB.disconnect()

    producer.shutdown()
