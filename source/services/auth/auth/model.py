import ormar
from services.auth.util.initdb import DB, META


class User(ormar.Model):
    class Meta:
        tablename: str = "openai_user"
        database = DB
        metadata = META

    id: int = ormar.Integer(primary_key=True, autoincrement=True)
    name: str = ormar.String(max_length=200)
    en_name: str = ormar.String(max_length=200, nullable=True)
    tenant_key: str = ormar.String(max_length=200, nullable=True)
    open_id: str = ormar.String(max_length=200, unique=True)
    union_id: str = ormar.String(max_length=200, nullable=True)
    user_id: str = ormar.String(max_length=200, nullable=True)
    avatar_url: str = ormar.String(max_length=200, nullable=True)
    access_token: str = ormar.String(max_length=200, nullable=True)
    tokens: int = ormar.Integer(default=0)
