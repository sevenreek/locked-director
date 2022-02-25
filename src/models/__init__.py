from pydantic import BaseModel
from datetime import datetime, date, timedelta
from enum import IntEnum

class GameTimerState(IntEnum):
    READY=0
    RUNNING=1
    PAUSED=2
    STOPPED=3

class GameTimer(BaseModel):
    started_on: datetime = None
    state: GameTimerState = GameTimerState.READY
    state_change_on: datetime = None
    seconds_remaining: int = None
    seconds_total: int = None