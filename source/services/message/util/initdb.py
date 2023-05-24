from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from services.message.util.settings import settings

DB_CONN = f'{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/' \
          f'{settings.DB_NAME}'

DB_POSTGRESQL_CONN = f'postgresql://{DB_CONN}'

engine = create_engine(
    DB_POSTGRESQL_CONN, echo=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=True)

Base = declarative_base(name='Base')


def get_db():
    """
    数据库配置
    :return: 数据库连接
    """
    db = SessionLocal()
    return db
