from fastapi import FastAPI
from routes.user import router
from fastapi.middleware.cors import CORSMiddleware
from core.exceptions import HTTPException, http_exception_handler, RequestValidationError, validation_exception_handler

from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )

    FastAPICache.init(
        RedisBackend(redis_client),
        prefix="fastapi-cache",
    )
    app.state.redis = redis_client
    yield

    await redis_client.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(router)