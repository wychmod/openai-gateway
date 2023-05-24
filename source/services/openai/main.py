import uvicorn
from fastapi import FastAPI

from basic.common.env_variable import get_integer_variable, get_string_variable
from services.openai.openai.api import router_openai

app = FastAPI(
    title='openapi管理',
    tags=["FastAPI openapi管理模块"],
)

app.include_router(router_openai, prefix='/openai', tags=['openai'])


if __name__ == '__main__':
    service_port = get_integer_variable('OPENAI_SERVICE_PORT', 8080)
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