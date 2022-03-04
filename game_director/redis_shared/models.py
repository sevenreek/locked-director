from pydantic import BaseModel
from datetime import datetime, date, timedelta
from enum import IntEnum
from typing import Optional, Union
class GameTimerState(IntEnum):
    READY=0
    RUNNING=1
    PAUSED=2
    STOPPED=3

class GameTimer(BaseModel):
    started_on: Optional[datetime] = None
    state: GameTimerState = GameTimerState.READY
    state_change_on: Optional[datetime] = None
    seconds_remaining: Union[None, int] = 0
    seconds_total: Union[None, int] = 0