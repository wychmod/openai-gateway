from typing import Optional

from pydantic import BaseModel

from services.auth.util.settings import settings


class AccessTokenReq(BaseModel):
    grant_type: str = "authorization_code"
    client_id: str = settings.APP_ID
    client_secret: str = settings.APP_SECRET
    code: Optional[str]
    redirect_uri: Optional[str] = f"{settings.AUTH_SERVICE_URL}/auth/callback/openai"


class UserDetailRes(BaseModel):
    name: str
    en_name: Optional[str]
    tenant_key: Optional[str]
    open_id: str
    union_id: Optional[str]
    user_id: Optional[str]
    avatar_url: Optional[str]
    access_token: str = ""
    tokens: int = 0


class UserTokensRes(BaseModel):
    name: str
    en_name: str
    open_id: str
    tokens: int
