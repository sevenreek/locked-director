from re import L
from typing import Awaitable, Callable
from aioredis import Redis
from aioredis.client import PubSub
from dotenv import load_dotenv
from os import getenv
from ..redis_shared import keys as rdk
from ..redis_shared import channels as rdch
from ..redis_shared import commands as rdcmd
from ..redis_shared.models import *
from ..redis_shared.util import init_game_timer
import asyncio
from typing import Union
from dataclasses import dataclass, asdict

@dataclass
class RedisMessage():
    topic: str
    data: str
    received_on: datetime

    @staticmethod
    def from_pubsub_message(m):
        return RedisMessage(
            topic=m["channel"],
            data=m['data'],
            received_on=datetime.now()
        )
class GameDirector():
    def __init__(self):


class RedisHandler():
    def __init__(self, redis: Redis, sleep_time: float = 0.01):
        self.redis = redis
        self.pubsub = redis.pubsub()
        self.active = False
        self.sleep_time = sleep_time
        self.handlers = {}
    
    async def init(self):
        await init_game_timer(self.redis)

    async def subscribe(self, channel:Union[str, list], handler:Callable):
        if type(channel) is str: channel = [channel]
        for ch in channel:
            existing_handlers = self.handlers.setdefault(ch, [])
        existing_handlers.append(handler)
        await self.pubsub.subscribe(*channel)

    async def loop(self):
        self.active = True
        while self.active:
            message = await self.pubsub.get_message(ignore_subscribe_messages=True)
            if message is not None:
                rm = RedisMessage.from_pubsub_message(message)
                self._handle_topic(rm)
            await asyncio.sleep(self.sleep_time)
        
    async def _handle_topic(self, topic, message):
        topic_handlers = [handler(self, message) for handler in self.handlers[topic]]
        await asyncio.gather(*topic_handlers)


    async def stop(self):
        self.active = False


async def game_timer_commands_handler(redis:Redis, msg:RedisMessage):
    (command, value) = msg.data.split(":")
    if(command == rdcmd.GAMETIMER_ADD):
        pass
    elif(command == rdcmd.GAMETIMER_PAUSE):
        pass
    elif(command == rdcmd.GAMETIMER_SET):
        pass
    elif(command == rdcmd.GAMETIMER_STOP):
        pass
    elif(command == rdcmd.GAMETIMER_START):
        pass


async def main():
    load_dotenv()
    redis_url = getenv("REDIS_URL", "redis://localhost")
    redis = Redis.from_url(redis_url, encoding = 'utf-8', decode_responses = True)
    redis_handler = RedisHandler(redis)
    await redis_handler.init()
    await redis_handler.subscribe(rdch.GAMETIMER_COMMAND, game_timer_commands_handler)
    print("Game director running!")
    await asyncio.gather(redis_handler.loop())

if __name__ == '__main__':
    asyncio.run(main())

