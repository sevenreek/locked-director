from re import L
from typing import Awaitable, Callable
from aioredis import Redis
from aioredis.client import PubSub
from dotenv import load_dotenv
from os import getenv
from ..redis_shared import keys as rdk
from ..redis_shared.models import *
from ..redis_shared.util import init_game_timer
import asyncio
from typing import Union
from dataclasses import dataclass, asdict

@dataclass
class RedisMessage():
    topic: str
    data: str
    timestamp: datetime

    @staticmethod
    def from_pubsub_message(m):
        return RedisMessage(
            topic=m["event"],
            data=m['data'],
            timestamp=datetime.now()
        )


class RedisHandler():
    def __init__(self, redis: Redis, sleep_time: float = 0.01):
        self.redis = redis
        self.pubsub = redis.pubsub()
        self.active = False
        self.sleep_time = sleep_time
        self.handlers = {}
    
    async def init(self):
        await init_game_timer(self.redis)

    async def subscribe(self, channel:Union[str, list], handler:Awaitable):
        if type(channel) is str: channel = [channel]
        existing_handlers = self.handlers.setdefault(channel, [])
        existing_handlers.append(handler)
        await self.pubsub.subscribe(*channel)

    async def loop(self):
        self.active = True
        while self.active:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                print(message)
                rm = RedisMessage.from_pubsub_message(message)
                print(rm)
            await asyncio.sleep(self.sleep_time)
        
    async def handle_topic(self, topic):
        if topic in self.handlers:
            await asyncio.gather(*self.handlers[topic])
            return True
        else:
            return False

    async def stop(self):
        self.active = False


async def main():
    load_dotenv()
    redis_url = getenv("REDIS_URL", "redis://redis")
    redis = Redis.from_url(redis_url, encoding = 'utf-8', decode_responses = True)
    redis_handler = RedisHandler(redis)
    redis_handler.init()
    await asyncio.gather(redis_handler.loop())

if __name__ == '__main__':
    asyncio.run(main())

