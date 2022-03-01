from aioredis import Redis
from .models import *
from . import keys as rdk

async def get_game_timer(redis:Redis) -> GameTimer:
    (started_on, state, state_change_on, seconds_remaining, seconds_total) = \
        await redis.mget(
            rdk.GAMETIMER_STARTED, 
            rdk.GAMETIMER_STATE,
            rdk.GAMETIMER_TIMESTAMP,
            rdk.GAMETIMER_REMAINING,
            rdk.GAMETIMER_TOTAL
        )
    game_timer = GameTimer(
        started_on = started_on,
        state = state,
        state_change_on = state_change_on,
        seconds_remaining = seconds_remaining,
        seconds_total = seconds_total
    )


async def init_game_timer(redis:Redis) -> GameTimer:
    await redis.setnx(rdk.GAMETIMER_STATE, GameTimerState.READY)
    return await get_game_timer(redis)