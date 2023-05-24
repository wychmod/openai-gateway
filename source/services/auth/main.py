import uvicorn
from fastapi import FastAPI
from fastapi_pagination import add_pagination

from basic.common.env_variable import get_integer_variable, get_string_variable
from services.auth.conversation.api import router_conversation
from services.auth.util.initdb import startup_event, shutdown_event
from services.auth.auth.api import router_auth, router_openai
from services.auth.message.api import router_message

app = FastAPI(
    title='网关管理',
    tags=["FastAPI openai-gateway管理模块"],
)
add_pagination(app)

# 配置数据库连接
app.add_event_handler("startup", startup_event)
app.add_event_handler("shutdown", shutdown_event)

# 注册路由
app.include_router(router_auth, prefix='/auth', tags=['auth'])
app.include_router(router_message, prefix='/message', tags=['message'])
app.include_router(router_openai, prefix='/openai', tags=['openai'])
app.include_router(router_conversation, prefix='/conversation', tags=['conversation'])


if __name__ == '__main__':
    service_port = get_integer_variable('OPENAI_SERVICE_PORT', 8000)
    debug = False if 'PRODUCTION' == get_string_variable('ENV', 'DEV') else True
    workers = get_integer_variable('SERVER_WORKERS', 2)
    # -workers INTEGER
    # Number of worker processes. Defaults to the $WEB_CONCURRENCY environment variable if available, or 1.
    # Not valid with --reload.
    uvicorn.run(
        'main:app', host='0.0.0.0', port=service_port,
        reload=debug,
        workers=workers
    )