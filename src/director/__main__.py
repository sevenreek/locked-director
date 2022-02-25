from typing import Awaitable, Callable
from aioredis import Redis
from aioredis.client import PubSub
from dotenv import load_dotenv
from os import getenv
import redis_shared.keys as rdk
from models import *
from redis_shared.util import init_game_timer
import asyncio
from typing import Union
from dataclasses import dataclass, asdict

@dataclass
class RedisMessage():
    topic: str
    data: str
    timestamp: datetime

class RedisHandler():
    def __init__(self, pubsub:PubSub, sleep_time: float = 0.01):
        self.pubsub = pubsub
        self.active = False
        self.sleep_time = sleep_time
        self.handlers = {}

    async def subscribe(self, channel:Union[str, list[str]], handler:Awaitable):
        if type(channel) is str: channel = [channel]
        existing_handlers = self.handlers.setdefault(channel, [])
        existing_handlers.append(handler)
        await self.pubsub.subscribe(*channel)

    async def loop(self):
        while self.active:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                print(message)
            asyncio.sleep(self.sleep_time)
        
    async def handle_topic(self, topic):
        if topic in self.handlers:
            await asyncio.gather(*self.handlers[topic])
            return True
        else:
            return False



async def main():

    load_dotenv()
    redis_url = getenv("REDIS_URL", "redis://redis")
    redis = Redis.from_url(redis_url, encoding='utf-8', decode_responses=True)
    game_timer = init_game_timer(redis)
    pub_sub = redis.pubsub()
    redis_handler = RedisHandler

if __name__ == '__main__':
    asyncio.run(main())

