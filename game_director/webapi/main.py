from aioredis import Redis
from aioredis.client import PubSub
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.params import Depends
from sse_starlette.sse import EventSourceResponse
from starlette.responses import JSONResponse as SSEJsonResponse
from dotenv import load_dotenv
from os import getenv
from ..redis_shared import keys as rdk

BASIC_CHANNELS = ["gametimer", "storypoint"]
GET_MESSAGE_TIMEOUT = 1.0

load_dotenv()
app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    redis_url = getenv("REDIS_URL", "redis://redis")
    redis = Redis.from_url(redis_url, encoding='utf-8', decode_responses=True)
    app.state.REDIS = redis


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await app.state.REDIS.close()


async def await_pubsub_updates(psub: PubSub, request: Request):
    while True:
        if await request.is_disconnected():
            break
        message = await psub.get_message(
            ignore_subscribe_messages=True,
            timeout=GET_MESSAGE_TIMEOUT
        )
        if message is not None:
            print(message)
            yield {
                'event': message['channel'],
                'data': message['data'],
                'retry': 500
            }
        # await asyncio.sleep(0.01)


async def depends_redis(req: Request) -> Redis:
    return req.app.state.REDIS


async def depends_redis_pubsub(redis: Redis = Depends(depends_redis)) -> PubSub:
    ps = redis.pubsub()
    try:
        yield ps
    finally:
        await ps.unsubscribe()
        await ps.close()


@app.get("/gametimer")
async def game_timer(redis: Redis = Depends(depends_redis)):
    (started_on, timer_state, state_timestamp, last_remaining, timer_total) = \
        await redis.mget(
            rdk.GAMETIMER_STARTED, 
            rdk.GAMETIMER_STATE,
            rdk.GAMETIMER_TIMESTAMP,
            rdk.GAMETIMER_REMAINING,
            rdk.GAMETIMER_TOTAL
        )
    return JSONResponse({
        "timer_started": started_on,
        "timer_state": timer_state,
        "timer_state_timestamp": state_timestamp,
        "timer_seconds": last_remaining,
        "timer_total": timer_total
    })


@app.get("/sse/basic")
async def subscribe_basic_updates(request:Request, pubsub:PubSub=Depends(depends_redis_pubsub)):
    await pubsub.subscribe(*BASIC_CHANNELS)
    event_generator = await_pubsub_updates(pubsub, request)
    return EventSourceResponse(event_generator)
"""
@app.websocket("/ws")
async def game_updates(websocket: WebSocket):
    return "ebin
"""